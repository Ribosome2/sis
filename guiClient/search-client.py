import io
import os

import wx
import requests
from wx.adv import TaskBarIcon as TaskBarIcon
confi_file_path = "image_searcher.conf"

import wx
print(wx.__file__)
def load_config():
    if not os.path.exists(confi_file_path):
        return ""
    with open(confi_file_path, 'r') as f:
        return f.read()


def save_config(svn_root_dir):
    with open(confi_file_path, 'w') as f:
        f.write(svn_root_dir)


class ImageUploader(wx.Frame):
    def __init__(self, parent, title):
        super(ImageUploader, self).__init__(parent, title=title, size=(600, 800))
        self.SetIcon(wx.Icon('./SIS_Icon.png', wx.BITMAP_TYPE_PNG))
        self.svn_root_dir = load_config()
        self.preview_texture_size = 80
        panel = wx.Panel(self)
        self.panel = panel
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.boxSizer = vbox

        head_sizer = wx.BoxSizer(wx.HORIZONTAL)
        upload_button = wx.Button(panel, label='选择图片搜索')
        upload_button.Bind(wx.EVT_BUTTON, self.on_upload)
        head_sizer.Add(upload_button, 0, wx.ALL | wx.LEFT, 5)

        search_clipboard_button = wx.Button(panel, label='搜索剪切板图片')
        search_clipboard_button.Bind(wx.EVT_BUTTON, self.on_search_clipboard)
        head_sizer.Add(search_clipboard_button, 0, wx.ALL | wx.LEFT, 5)

        self.image_ctrl = wx.StaticBitmap(panel, bitmap=wx.NullBitmap,
                                          size=(self.preview_texture_size, self.preview_texture_size))
        head_sizer.Add(self.image_ctrl, 0, wx.ALL | wx.CENTER)

        vbox.Add(head_sizer, 0, wx.ALL | wx.LEFT, 5)

        self.scrolled_window = wx.ScrolledWindow(panel)
        self.imageListSizer = wx.BoxSizer(wx.VERTICAL)
        self.scrolled_window.SetSizer(self.imageListSizer)
        vbox.Add(self.scrolled_window, 1, wx.EXPAND | wx.ALL, 5)  # Add the scrolled window to the main sizer

        panel.SetSizer(vbox)

    def set_search_image(self, image):
        image = self.clamp_image_size(image, self.preview_texture_size)
        bitmap = wx.Bitmap(image)
        self.image_ctrl.SetBitmap(bitmap)
        self.image_ctrl.SetInitialSize(size=(image.GetWidth(), image.GetHeight()))

    def search_image_file(self, files):
        data = {'isSVN': 'true', 'resultAsText': 'true'}
        try:
            response = requests.post('http://172.16.12.41:5000', files=files, data=data)
            if response.status_code == 200:
                result_text = response.text  # 获取服务器返回的字符串
                # print(result_text)  # 打印返回的字符串
                paths = result_text.split('\n')  # 按换行符分割成列表

                # libpng "iCCP: known incorrect sRGB profile" 直接弹窗很烦,https://github.com/wrye-bash/wrye-bash/issues/458
                wx.Log.EnableLogging(enable=False)
                self.load_and_show_images(paths)
                wx.Log.EnableLogging(enable=True)
                # wx.MessageBox("Upload successful", "Success", wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox("Upload failed", "Error", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox("Upload failed:" + str(e), "Error", wx.OK | wx.ICON_ERROR)

    def check_svn_root_setup(self):
        if self.svn_root_dir == "":
            dlg = wx.DirDialog(self, "请选择SVN根目录(本地展示搜索图片结果用)", style=wx.DD_DEFAULT_STYLE)
            if dlg.ShowModal() == wx.ID_OK:
                self.svn_root_dir = dlg.GetPath()
                save_config(self.svn_root_dir)
            dlg.Destroy()
            return True
        else:
            return False

    def on_search_clipboard(self, event):
        if self.check_svn_root_setup():
            return
        if wx.TheClipboard.Open():
            if wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_BITMAP)):
                data = wx.BitmapDataObject()
                wx.TheClipboard.GetData(data)
                big_map = data.GetBitmap()
                image = wx.Image(big_map.ConvertToImage())
                self.set_search_image(image)
                image = wx.Image(big_map.ConvertToImage())
                tempFileName = "tempClipboardImage.png"
                image.SaveFile(tempFileName, wx.BITMAP_TYPE_PNG)
                files = {'query_img': open(tempFileName, 'rb')}
                self.search_image_file(files)
            else:
                wx.MessageBox("剪切板没图片", "Error", wx.OK | wx.ICON_ERROR)
        else:
            wx.MessageBox("剪切板打开失败", "Error", wx.OK | wx.ICON_ERROR)

    def on_upload(self, event):
        if self.check_svn_root_setup():
            return
        with wx.FileDialog(self, "选择要搜索的PNG图片", wildcard="PNG files (*.png)|*.png",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            image = wx.Image(pathname, wx.BITMAP_TYPE_ANY)
            self.set_search_image(image)
            files = {'query_img': open(pathname, 'rb')}
            self.search_image_file(files)

    def clamp_image_size(self, image, max_size):
        if image.GetWidth() > max_size or image.GetHeight() > max_size:
            if image.GetWidth() > image.GetHeight():
                new_width = max_size
                new_height = int(max_size * image.GetHeight() / image.GetWidth())
            else:
                new_height = max_size
                new_width = int(max_size * image.GetWidth() / image.GetHeight())
            image = image.Scale(new_width, new_height, wx.IMAGE_QUALITY_HIGH)
        return image

    def load_and_show_images(self, paths):
        # self.imageListSizer.Clear()

        for child in self.scrolled_window.GetChildren():
            child.Destroy()
        for path in paths:
            if path == "":
                continue
            path = self.svn_root_dir + "/" + path
            if path != "" and os.path.exists(path):
                image = wx.Image(path, wx.BITMAP_TYPE_ANY)
                if image.IsOk():
                    self.add_single_image_result(image, path)
                else:
                    print("Invalid image format or path:", path)
            else:
                print("File not found at path:", path)

        self.scrolled_window.SetScrollRate(15, 15)  # Set the scrolling rate
        self.scrolled_window.SetVirtualSize((600, len(paths) * 100))
        self.scrolled_window.Scroll(0, 0)

    def add_single_image_result(self, image, path):
        size_desc = "大小:" + str(image.GetWidth()) + "X" + str(image.GetHeight())
        image = self.clamp_image_size(image, 300)
        bmp = wx.Bitmap(image)
        static_image = wx.StaticBitmap(self.scrolled_window, -1, bmp, (10, 10))
        item_sizer = wx.BoxSizer(wx.HORIZONTAL)
        vertical_sizer = wx.BoxSizer(wx.VERTICAL)
        item_sizer.Add(static_image, 0, wx.ALL | wx.LEFT, 5)
        item_sizer.Add(vertical_sizer, 0, wx.ALL | wx.LEFT, 5)
        absolute_path = os.path.abspath(path)
        vertical_sizer.Add(wx.StaticText(self.scrolled_window, label=absolute_path), 0, wx.ALL | wx.Right, 5)
        vertical_sizer.Add(wx.StaticText(self.scrolled_window, label=size_desc), 0, wx.ALL | wx.Right, 5)

        open_file_button = wx.Button(self.scrolled_window, label='打开文件')
        open_file_button.Bind(wx.EVT_BUTTON, lambda event: os.startfile(path))
        vertical_sizer.Add(open_file_button, 0, wx.ALL | wx.RIGHT, 5)

        open_folder_button = wx.Button(self.scrolled_window, label='打开文件夹')
        open_folder_button.Bind(wx.EVT_BUTTON, lambda event: os.startfile(os.path.dirname(absolute_path)))
        vertical_sizer.Add(open_folder_button, 0, wx.ALL | wx.RIGHT, 5)
        self.imageListSizer.Add(item_sizer, 0, wx.ALL | wx.LEFT, 5)  # 将图片添加到垂直布局管理器中


if __name__ == '__main__':
    print("Kyle Image Searcher Started")
    app = wx.App()
    frame = ImageUploader(None, "ImageSearcher")
    frame.Show()
    app.MainLoop()
