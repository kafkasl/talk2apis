import logging
import os

import litellm
import openai
from aiolimiter import AsyncLimiter
from litellm import acompletion
from litellm import RateLimitError
from litellm.exceptions import APIError

# from openai.error import APIError, RateLimitError, Timeout, TryAgain
from retry import retry

# Configure the logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

AI_TIMEOUT = 90  # seconds

OPENAI_RETRIES = 5
MAX_REQS_MINUTE = 60


class AiHandler:
    """
    This class handles interactions with the OpenAI API for chat completions.
    It initializes the API key and other settings from a configuration file,
    and provides a method for performing chat completions using the OpenAI ChatCompletion API.
    """

    def __init__(self, model="gpt-4-turbo-preview"):
        """
        Initializes the OpenAI API key and other settings from a configuration file.
        Raises a ValueError if the OpenAI key is missing.
        """
        self.limiter = AsyncLimiter(MAX_REQS_MINUTE)
        try:
            openai.api_key = os.getenv("OPENAI_API_KEY")
            litellm.openai_key = os.getenv("OPENAI_API_KEY")

        except AttributeError as e:
            raise ValueError("OpenAI key is required") from e

    @retry(
        exceptions=(AttributeError, RateLimitError),
        tries=OPENAI_RETRIES,
        delay=2,
        backoff=2,
        jitter=(1, 3),
    )
    async def chat_completion(
        self,
        model: str,
        system: str,
        user: str,
        temperature: float = 0.2,
        frequency_penalty: float = 0.0,
    ):
        try:
            async with self.limiter:
                logger.info("-----------------")
                logger.info("Running inference ...")
                logger.info(f"system:\n{system}")
                logger.info(f"user:\n{user}")

                response = await acompletion(
                    model=model,
                    deployment_id=None,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=temperature,
                    frequency_penalty=frequency_penalty,
                    force_timeout=AI_TIMEOUT,
                )
        except APIError as e:
            logging.error("Error during OpenAI inference ", e)
            raise
        except RateLimitError as e:
            logging.error("Rate limit error during OpenAI inference ", e)
            raise
        except Exception as e:
            logging.error("Unknown error during OpenAI inference: ", e)
            raise APIError from e
        if response is None or len(response["choices"]) == 0:
            raise APIError
        resp = response["choices"][0]["message"]["content"]
        finish_reason = response["choices"][0]["finish_reason"]
        logger.debug(f"response:\n{resp}")
        logger.info("done")
        logger.info("-----------------")
        return resp, finish_reason
