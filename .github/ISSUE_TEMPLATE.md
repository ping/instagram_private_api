## Please follow the guide below

- Issues submitted without this template format will be **ignored**.
- You will be asked some questions and requested to provide some information, please read them **carefully** and answer completely.
- Do not post screenshots of error messages or code.
- Put an `x` into all the boxes [ ] relevant to your issue (like so [x] no spaces).
- Use the *Preview* tab to see how your issue will actually look like.
- Issues about reverse engineering is out of scope and will be closed without response.

---

### Before submitting an issue, make sure you have:
- [ ] Updated to the lastest version v1.3.5
- [ ] Read the [README](https://github.com/ping/instagram_private_api/blob/master/README.md) and [docs](https://instagram-private-api.readthedocs.io/en/latest/)
- [ ] [Searched](https://github.com/ping/instagram_private_api/search?type=Issues) the bugtracker for similar issues including **closed** ones
- [ ] Reviewed the sample code in [tests](https://github.com/ping/instagram_private_api/tree/master/tests) and [examples](https://github.com/ping/instagram_private_api/tree/master/examples)

### Which client are you using?
- [ ] app (``instagram_private_api/``)
- [ ] web (``instagram_web_api/``)

### Purpose of your issue?
- [ ] Bug report (encountered problems/errors)
- [ ] Feature request (request for a new functionality)
- [ ] Question
- [ ] Other

---

### The following sections requests more details for particular types of issues, you can remove any section (the contents between the triple ---) not applicable to your issue.

---

### For a *bug report*, you **must** include the Python version used, *code* that will reproduce the error, and the *error log/traceback*.

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

---

### For a new endpoint *feature request*, you should include the *capture of the request and response*.

Request:

```http
# Please provide your capture below
GET /api/v1/si/fetch_headers/?guid=123456abcdeff19cc2f123456&challenge_type=signup HTTP/1.1
Host: i.instagram.com
Connection: keep-alive
X-IG-Connection-Type: mobile(UMTS)
X-IG-Capabilities: 3ToAAA==
Accept-Language: en-US
Cookie: csrftoken=g79dofDBlVEA37II3LI7YdHeiMrd9ylj; mid=WFI52QABAAGrbKL-OZ4DtgLd9QIf
User-Agent: Instagram 10.3.0 Android (18/4.3; 320dpi; 720x1280; Xiaomi; HM 1SW; armani; qcom; en_US)
Accept-Encoding: gzip, deflate, sdch
```

Response:

```http
# Please provide your capture below
HTTP/1.1 200 OK
Content-Language: en
Expires: Sat, 01 Jan 2000 00:00:00 GMT
Vary: Cookie, Accept-Language
Pragma: no-cache
Cache-Control: private, no-cache, no-store, must-revalidate
Date: Thu, 15 Dec 2016 08:50:19 GMT
Content-Type: application/json
Set-Cookie: csrftoken=g79dofABCDEFGII3LI7YdHei1234567; expires=Thu, 14-Dec-2017 08:50:19 GMT; Max-Age=31449600; Path=/; secure
Connection: keep-alive
Content-Length: 16

{"status": "ok"}
```
---

### Describe your issue

Explanation of your issue goes here. Please make sure the description is worded well enough to be understood with as much context and examples as possible.
