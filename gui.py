import ui
import dialogs
import ssdp
import huawei_api

GATEWAYIP = ""
USER = "admin"
PASSWD = "hu4757"

def create_instance(ip):
	global HUAWEI
	HUAWEI = huawei_api.Client(ip, USER, PASSWD)

def find_device(ctx, indicator=None):
  if indicator:
    indicator.start()
  devices = ssdp.get_devices(st="urn:schemas-upnp-org:device:InternetGatewayDevice:1", field='modelDescription', name="Huawei", timeout=3)
  if not devices:
    ctx["devices_btn"].title = "No device found"
  elif len(devices) == 1:
    ctx["devices_btn"].title = f"{devices[0][1]}: {devices[0][0]}"
    create_instance(devices[0][0])
  else:
    selector = dialogs.list_dialog(title='Devices found:', items=[f"{i[1]}: {i[0]}"
                 for i in devices])
    if selector:
      items = selector.split(": ")
      ctx["devices_btn"].title = f"{items[1]}: {items[0]}"
      create_instance(items[1])
  if indicator:
    indicator.stop()

def select_tab(ctx, new_tab):
  global SUBVIEW
  ctx.superview.remove_subview(SUBVIEW)
  SUBVIEW = ui.load_view(f'ui/tab_{new_tab}')
  SUBVIEW.frame = ctx.superview["subviews"].frame
  ctx.superview.add_subview(SUBVIEW)

def segmented_control(ctx):
  select_tab(ctx, ctx.selected_index)

def button_press(sender):
  global HTTP_PARAMS
  global INDICATOR
  if sender.name == "devices_btn":
    find_device(sender.superview, INDICATOR)
  elif sender.name == "btn_getstatus":
    sender.superview["textview1"].text = str(HUAWEI.status())
  elif sender.name == "btn_sms_send":
    HUAWEI.send_sms(sender.superview["sms_number"].text, sender.superview["sms_content"].text)
    sender.enabled = False

def main():
  v = ui.load_view('ui/main')
  global SUBVIEW
  SUBVIEW = ui.load_view('ui/tab_0')
  SUBVIEW.frame = v["subviews"].frame 
  v.add_subview(SUBVIEW)
  v.present()
  
  global INDICATOR
  INDICATOR = ui.ActivityIndicator()
  INDICATOR.x, INDICATOR.y = (12, 12)
  v.add_subview(INDICATOR)
  find_device(v, INDICATOR)
 
if __name__ == '__main__':
  main()
