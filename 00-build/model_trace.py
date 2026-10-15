"""Record observable model requests and responses, without client credentials."""

import json
import logging


LOGGER = logging.getLogger("cortex.trace")


def complete(client, *, role: str, **request):
    """Call Chat Completions and log the exact payload and returned response."""
    def encode(value):
        return value.model_dump(mode="json", exclude_none=True)

    LOGGER.info("\n%s MODEL REQUEST\n%s", role.upper(),
                json.dumps(request, indent=2, ensure_ascii=False, default=encode))
    response = client.chat.completions.create(**request)
    LOGGER.info("\n%s MODEL RESPONSE (includes token usage)\n%s", role.upper(),
                json.dumps(response.model_dump(mode="json", exclude_none=True),
                           indent=2, ensure_ascii=False))
    return response
