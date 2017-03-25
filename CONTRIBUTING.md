# Contributing

## Issues
When submitting an [issue report](https://github.com/ping/instagram_private_api/issues/new), please make sure to fill up the details as specified in the [issue template](.github/ISSUE_TEMPLATE.md).

> This is a strict requirement, and failure to do so will get your issue closed without response.

## Pull Requests
Here are a few simple guidelines to follow if you wish to submit a pull request:

- [**Submit an Issue**](https://github.com/ping/instagram_private_api/issues/new) (mark as "Other") describing what you intend to implement if it's a substantial change. Allow me time to provide feedback so that there is less risk of rework or rejection.
- New endpoints should be accompanied by a **relevant test case**.
- Backward compatibility should not be broken without very good reason.
- I try to maintain a **small dependency footprint**. If you intend to add a new dependency, make sure that there is a strong case for it.
- Run ``flake8 --max-line-length=120`` on your changes before pushing.
- Make sure docs are buildable by running ``make html`` in the ``docs/`` folder (after you've installed the dev requirements).
- **Please do not take a rejection of a PR personally**. I appreciate your contribution but I reserve the right to be the final arbiter for any changes. You're free to fork my work and tailor it for your needs, it's fine!

Thank you for your interest. 
