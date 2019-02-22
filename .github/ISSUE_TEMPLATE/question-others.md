---
name: Question/Others
about: Not an error or feature request

---

## Please follow the guide below

- Issues submitted without this template format will be **ignored**.
- Rlease read them **carefully** and answer completely.
- Do not post screenshots of error messages or code.
- Put an `x` into all the boxes [ ] relevant to your issue (==> [x] *no* spaces).
- Use the *Preview* tab to see how your issue will actually look like.
- Issues about reverse engineering is out of scope and will be closed without response.
- Any mention of spam-like actions or spam-related tools/libs/etc is strictly **not allowed**.

---

### Before submitting an issue, make sure you have:
- [ ] Updated to the lastest version v1.6.0
- [ ] Read the [README](https://github.com/ping/instagram_private_api/blob/master/README.md) and [docs](https://instagram-private-api.readthedocs.io/en/latest/)
- [ ] [Searched](https://github.com/ping/instagram_private_api/search?type=Issues) the bugtracker for similar issues including **closed** ones
- [ ] Reviewed the sample code in [tests](https://github.com/ping/instagram_private_api/tree/master/tests) and [examples](https://github.com/ping/instagram_private_api/tree/master/examples)

### Which client are you using?
- [ ] app (``instagram_private_api/``)
- [ ] web (``instagram_web_api/``)

---

### Describe your Question/Issue:

Please make sure the description is worded well enough to be understood with as much context and examples as possible.

---

Paste the output of ``python -V`` here:

Code:

```python
# Example code that will produce the error reported
from instagram_web_api import Client

web_api = Client()
user_feed_info = web_api.user_feed('1234567890', count=10)
```

Error/Debug Log:

```python
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ZeroDivisionError: integer division or modulo by zero
```
