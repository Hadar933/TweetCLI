import os
import unittest
from unittest.mock import patch

os.environ["TWEETCLI_BACKEND"] = "xquik"
os.environ["XQUIK_API_KEY"] = "xq_test"
os.environ["XQUIK_ACCOUNT"] = "@example"

import tweet


class FakeResponse:
    def __init__(self, status_code, data, headers=None):
        self.status_code = status_code
        self._data = data
        self.headers = headers or {}

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, post_response, get_responses=None):
        self.post_response = post_response
        self.get_responses = list(get_responses or [])
        self.post_calls = []
        self.get_calls = []

    def post(self, url, **kwargs):
        self.post_calls.append((url, kwargs))
        return self.post_response

    def get(self, url, **kwargs):
        self.get_calls.append((url, kwargs))
        return self.get_responses.pop(0)


class TweetSplitTests(unittest.TestCase):
    def test_split_preserves_hard_boundary_characters(self):
        original = "a" * (tweet.MAX_TWEET_LEN + 10)

        parts = tweet._split_tweet(original)
        reconstructed = "".join(
            part.removesuffix(tweet.SEE_NEXT_TWEET) for part in parts
        )

        self.assertEqual(reconstructed, original)

    def test_split_preserves_punctuation(self):
        original = "a" * 100 + "." + "b" * 200

        parts = tweet._split_tweet(original)
        reconstructed = "".join(
            part.removesuffix(tweet.SEE_NEXT_TWEET) for part in parts
        )

        self.assertEqual(reconstructed, original)


class XquikWriteTests(unittest.TestCase):
    def test_posts_with_idempotency_and_returns_confirmed_tweet_id(self):
        response = FakeResponse(
            200,
            {
                "action": "create_tweet",
                "terminal": True,
                "success": True,
                "tweetId": "123",
                "id": "write-action",
            },
        )
        session = FakeSession(response)

        tweet_id = tweet._post_xquik_tweet("Hello", session)

        self.assertEqual(tweet_id, "123")
        self.assertEqual(len(session.post_calls), 1)
        _, request = session.post_calls[0]
        self.assertEqual(request["headers"]["x-api-key"], "xq_test")
        self.assertIn("Idempotency-Key", request["headers"])
        self.assertEqual(
            request["json"],
            {"account": "@example", "text": "Hello"},
        )

    def test_polls_accepted_write_without_submitting_again(self):
        accepted = FakeResponse(
            202,
            {
                "terminal": False,
                "writeActionId": "action-1",
                "statusUrl": "/api/v1/x/write-actions/action-1",
                "pollAfterMs": 100,
            },
        )
        completed = FakeResponse(
            200,
            {
                "action": "create_tweet",
                "terminal": True,
                "success": True,
                "targetId": "456",
            },
        )
        session = FakeSession(accepted, [completed])

        with patch("tweet.time.sleep") as sleep:
            tweet_id = tweet._post_xquik_tweet("Hello", session)

        self.assertEqual(tweet_id, "456")
        self.assertEqual(len(session.post_calls), 1)
        self.assertEqual(
            session.get_calls[0][0],
            "https://xquik.com/api/v1/x/write-actions/action-1",
        )
        sleep.assert_called_once_with(0.1)

    def test_rejects_cross_origin_poll_url(self):
        response = FakeResponse(
            202,
            {
                "terminal": False,
                "writeActionId": "action-1",
                "statusUrl": "https://example.com/api/v1/x/write-actions/action-1",
                "pollAfterMs": 100,
            },
        )
        session = FakeSession(response)

        with (
            patch("tweet.time.sleep"),
            self.assertRaisesRegex(ValueError, "unsafe status URL"),
        ):
            tweet._post_xquik_tweet("Hello", session)

        self.assertEqual(session.get_calls, [])

    def test_does_not_treat_write_action_id_as_tweet_id(self):
        response = FakeResponse(
            200,
            {
                "action": "create_tweet",
                "terminal": True,
                "success": True,
                "id": "write-action",
            },
        )
        session = FakeSession(response)

        with self.assertRaisesRegex(ValueError, "confirmed tweet ID"):
            tweet._post_xquik_tweet("Hello", session)

    def test_xquik_backend_does_not_require_twitter_credentials(self):
        with patch("tweet._post_xquik_tweet", return_value="123") as post_tweet:
            tweet.post(
                "Hello",
                username="ignored",
                media_paths=[],
                verbose=False,
                screenshot_path="",
                automatic=True,
            )

        post_tweet.assert_called_once_with("Hello")


if __name__ == "__main__":
    unittest.main()
