def test_import():
    from instapi import Client
    from instapi import ClientCompatPatch
    from instapi import (
        ClientError, ClientLoginError, ClientLoginRequiredError,
        ClientCookieExpiredError, ClientThrottledError, ClientConnectionError,
        ClientCheckpointRequiredError, ClientChallengeRequiredError,
        ClientSentryBlockError, ClientReqHeadersTooLargeError,
    )
    from instapi import MediaRatios
    from instapi import MediaTypes

    from instapi.utils import (
        InstagramID, gen_user_breadcrumb,
        max_chunk_size_generator, max_chunk_count_generator, get_file_size,
        ig_chunk_generator
    )
    from instapi.constants import Constants
    from instapi.compat import compat_urllib_parse
    from instapi.compat import compat_urllib_error

    assert True == True