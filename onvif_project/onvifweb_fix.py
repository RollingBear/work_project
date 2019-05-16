# _*_coding:utf-8_*_
import sys
import bottle
from bottle import response, request, post
from onvif import ONVIFCamera
import zeep
import logging
from logging.handlers import RotatingFileHandler
import traceback
import time
import json
from gevent import monkey

monkey.patch_all()

# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
#                     stream=sys.stdout)
#
# # 定义按文件大小切割日志
# logger = logging.getLogger()
# Rthandler = RotatingFileHandler(sys.path[0] + '/log.log', maxBytes=10, backupCount=5)
# Rthandler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
# Rthandler.setFormatter(formatter)
# logger.addHandler(Rthandler)

app = bottle.Bottle()
bottle.BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024  #


def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue


zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue

XMAX = 1
XMIN = -1
YMAX = 1
YMIN = -1
ZMAX = 1
ZMIN = -1
FMAX = 1
FMIN = -1

control_dict = {'PanTilt': {'_x': 0.00, '_y': 0.00}, 'Zoom': {'_x': 0.00}}


# 摄像头控制
def perform_move(ptz, request, timeout):
    # Start continuous move
    ptz.ContinuousMove(request)
    # Wait a certain time
    time.sleep(timeout)
    # Stop continuous move
    ptz.Stop({'ProfileToken': request.ProfileToken})


# 摄像头上转
def move_up(ptz, request, timeout=1):
    print('move up...')
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = YMAX
    perform_move(ptz, request, timeout)


# 摄像头下转
def move_down(ptz, request, timeout=1):
    print('move down...')
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = YMIN
    perform_move(ptz, request, timeout)


# 摄像头右转
def move_right(ptz, request, timeout=1):
    print('move right...')
    request.Velocity.PanTilt._x = XMAX
    request.Velocity.PanTilt._y = 0
    perform_move(ptz, request, timeout)


# 摄像头左转
def move_left(ptz, request, timeout=1):
    print('move left...')
    request.Velocity.PanTilt._x = XMIN
    request.Velocity.PanTilt._y = 0
    perform_move(ptz, request, timeout)


# 摄像头右上转
def move_right_up(ptz, request, timeout=1):
    print('move rightup...')
    request.Velocity.PanTilt._x = XMAX
    request.Velocity.PanTilt._y = YMAX
    perform_move(ptz, request, timeout)


# 摄像头左上转
def move_left_up(ptz, request, timeout=1):
    print('move leftup...')
    request.Velocity.PanTilt._x = XMIN
    request.Velocity.PanTilt._y = YMAX
    perform_move(ptz, request, timeout)


# 摄像头右上转
def move_right_down(ptz, request, timeout=1):
    print('move rightdown...')
    request.Velocity.PanTilt._x = XMAX
    request.Velocity.PanTilt._y = YMIN
    perform_move(ptz, request, timeout)


# 摄像头左上转
def move_left_down(ptz, request, timeout=1):
    print('move leftdown...')
    request.Velocity.PanTilt._x = XMIN
    request.Velocity.PanTilt._y = YMIN
    perform_move(ptz, request, timeout)


# 摄像头调焦拉近
def move_zoomin(ptz, request, timeout=1):
    print('move Zoomin...')
    request.Velocity.Zoom._x = ZMAX
    perform_move(ptz, request, timeout)


# 摄像头调焦拉远
def move_zoomout(ptz, request, timeout=1):
    print('move Zoomout...')
    request.Velocity.Zoom._x = ZMIN
    perform_move(ptz, request, timeout)


# 摄像头图像控制
def img_move(img, request, timeout):
    # Start continuous move
    img.Move(request)
    # Wait a certain time
    time.sleep(timeout)
    # Stop continuous move
    img.Stop({'VideoSourceToken ': request.VideoSourceToken})


# 摄像头聚焦拉近
def move_focusin(img, request, timeout=1):
    print('move focusin...')
    request.Focus.Continuous._x = XMAX
    img_move(img, request, timeout)


# 摄像头聚焦拉远
def move_focusout(img, request, timeout=1):
    print('move focusout...')
    request.Focus.Continuous._x = XMIN
    img_move(img, request, timeout)


# 摄像头光圈放大
def move_irisin(img, request, timeout=1):
    print('move irisin...')
    request.Focus.Continuous._x = XMAX
    img_move(img, request, timeout)


# 摄像头光圈缩小
def move_irisout(img, request, timeout=1):
    print('move irisout...')
    request.Focus.Continuous._x = XMIN
    img_move(img, request, timeout)


# 摄像头控制
def continuous_move(action, ip, port, username, password):
    try:
        mycam = ONVIFCamera(ip, port, username, password)
        # Create media service object
        media = mycam.create_media_service()
        # Create ptz service object
        ptz = mycam.create_ptz_service()

        # Get target profile
        media_profile = media.GetProfiles()[0]

        # Get PTZ configuration options for getting continuous move range
        request = ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = media_profile.PTZConfiguration.token
        ptz_configuration_options = ptz.GetConfigurationOptions(request)

        print(ptz_configuration_options)

        # print('Service Capabilities: ', ptz.GetServiceCapabilities()['_attr_1'])
        # print('result move: ', ptz.GetStatus())

        request = ptz.create_type('ContinuousMove')
        request.ProfileToken = media_profile.token
        # request.Velocity = control_dict
        # request_ptz.Velocity = media_profile
        # print(media_profile)
        # print()
        # print(request_ptz)

        ptz.Stop({'ProfileToken': media_profile.token})

        # Get range of pan and tilt
        # NOTE: X and Y are velocity vector
        global XMAX, XMIN, YMAX, YMIN, ZMAX, ZMIN
        XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
        XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
        YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
        YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min
        ZMAX = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].XRange.Max
        ZMIN = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].XRange.Min

        if action == 'up':
            move_up(ptz, request)
        elif action == 'down':
            move_down(ptz, request)
        elif action == 'left':
            move_left(ptz, request)
        elif action == 'right':
            move_right(ptz, request)
        return True
    except Exception as e:
        # logger.error(traceback.format_exc())
        logging.info(traceback.format_exc())
        return False


def continuous_scene(action, ip, port, username, password):
    try:
        camera = ONVIFCamera(ip, port, username, password)

        media = camera.create_media_service()

        ptz = camera.create_ptz_service()
        media_profile = media.GetProfiles()[0]

        request = ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = media_profile.PTZConfiguration.token
        ptz_configuration_options = ptz.GetConfigurationOptions(request)

        request = ptz.create_type('ContinuousMove')
        request.ProfileToken = media_profile.token

        ptz.Stop({'ProfileToken': media_profile.token})

        global XMAX, XMIN, YMAX, YMIN, ZMAX, ZMIN, FMAX, FMIN

        ZMAX = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].XRange.Max
        ZMIN = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].XRange.Min

        if action == '':
            move_zoomin(ptz, request)
        elif action == '':
            move_zoomout(ptz, request)

        return True
    except:
        # logger.error(traceback.format_exc())
        logging.info(traceback.format_exc())
        return False


# 摄像头控制(未完成)
def continuous_imgae_move(action, ip, port, username, password):
    try:
        mycam = ONVIFCamera(ip, port, username, password)
        # Create media service object
        media = mycam.create_imaging_service()
        # Create ptz service object
        imaging = mycam.create_imaging_service()

        # Get target profile
        media_profile = media.GetProfiles()[0]

        # Get PTZ configuration options for getting continuous move range
        request = imaging.create_type('GetMoveOptions')
        request.ConfigurationToken = media_profile.VideoSourceConfiguration.token
        imaging_configuration_options = imaging.GetMoveOptions(request)

        request = imaging.create_type('Move')
        request.VideoSourceToken = media_profile.VideoSourceConfiguration.token

        imaging.Stop({'VideoSourceToken ': media_profile.VideoSourceConfiguration.token})

        # Get range of pan and tilt
        # NOTE: X and Y are velocity vector
        global FMAX, FMIN
        FMAX = imaging_configuration_options.Continuous.Speed[0].Max
        FMIN = imaging_configuration_options.Continuous.Speed[0].Min

        if action == 'up':
            move_up(imaging, request)
        elif action == 'down':
            move_down(imaging, request)
        elif action == 'left':
            move_left(imaging, request)
        elif action == 'right':
            move_right(imaging, request)
        return True
    except Exception as e:
        # logger.error(traceback.format_exc())
        logging.info(traceback.format_exc())
        return False


# 生成带验证的rtsp地址
def make_uri_withauth(uri, username, password):
    newuri = uri[:7] + str(username) + ':' + str(password) + '@' + uri[7:]
    return newuri


@app.route('/getrtspurl', method='POST')
def getrtspurl():
    """
        接收参数：json格式
        POST
        {'ip': '', 'port': '', 'username': '', 'password': '','is_auth':''}
        :return:
    """
    try:
        response.content_type = "application/json"
        data = request.json
        ip = data['ip']
        port = int(data['port'])
        username = data['username']
        password = data['password']
        is_auth = data['is_auth']
        mycam = ONVIFCamera(ip, port, username, password)
        media_service = mycam.create_media_service()
        profiles = media_service.GetProfiles()
        token = profiles[0].token
        uri = media_service.GetStreamUri(
            {'StreamSetup': {'Stream': 'RTP_unicast', 'Transport': {'Protocol': 'RTSP'}}, 'ProfileToken': token})
        # print(uri)
        if is_auth:
            rtspurl = make_uri_withauth(uri['Uri'], username, password)
        else:
            rtspurl = uri
        return json.dumps({'rtspurl': rtspurl})
    except Exception as e:
        # logger.error(traceback.format_exc())
        logging.info(traceback.format_exc())
        return json.dumps({'rtspurl': 'error'})


@app.route('/cameracontrol', method='POST')
def cameracontrol():
    """
        接收参数：json格式 POST
        {'ip':'','port':'','username':'','password':'','action':''}
        :return:
    """
    try:
        response.content_type = "application/json"
        data = request.json
        ip = data['ip']
        port = int(data['port'])
        username = data['username']
        password = data['password']
        action = data['action']
        res = continuous_move(action, ip, port, username, password)
        return json.dumps({'res': res})
    except Exception as e:
        # logger.error(traceback.format_exc())
        logging.info(traceback.format_exc())
        return json.dumps({'res': "error"})


def start():
    bottle.run(app,
               # server='gevent',
               # host="0.0.0.0",
               host="127.0.0.1",
               port=9898, reloader=True, debug=True)


if __name__ == "__main__":
    start()
