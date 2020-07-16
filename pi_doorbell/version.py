

__name          = "pi_doorbell"
__version       = "3.2"
__description   = "Raspberry Pi Doorbell Notifications Service for Home-Assistant"
__author        = "Josh.5"
__email         = "jsunnex@gmail.com"
__disclaimer    = ""
__forum         = ""
__video         = ""
__website       = "http://streamingtech.tv/""http://streamingtech.tv/"



__author__      = '%s (%s)' % (__author, __email)
__version__     = __version




def read_info():
    return {
          "name" :          __name
        , "version" :       __version
        , "description" :   __description
        , "author" :        __author
        , "email" :         __email
        , "disclaimer" :    __disclaimer
        , "forum" :         __forum
        , "video" :         __video
        , "website" :       __website
    }