def common(request):
    if 'optionall-cookie-info' in request.COOKIES:
        cookies_info = request.COOKIES['optionall-cookie-info']
    else:
        cookies_info = 0

    cmm = {

        'cookies_info': cookies_info,

    }
    return cmm
