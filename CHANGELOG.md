# Change Log

## 1.0.6 (pending)
- Support specification of location to post_photo

## 1.0.5
- New disable/enable media comments endpoints
- New FB location search endpoint

## 1.0.4
- Add new settings property to help extract settings for saving

## 1.0.3
- Fix Python 3 compatibility

## 1.0.2
- Detect if authenticated cookie has expired and raise ClientCookieExpiredError

## 1.0.1
- Detect if re-login is required and raise ClientLoginRequiredError

## 1.0.0

First release

- access both the private Instagram app or web API
- CompatPatch patches the objects returned in the private API to match those returned in the public API
- can be used to largely replace the public Instagram API that is now severely restricted
