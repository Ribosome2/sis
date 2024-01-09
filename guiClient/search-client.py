import os

import wx
import requests


class ImageUploader(wx.Frame):
    def __init__(self, parent, title):
        super(ImageUploader, self).__init__(parent, title=title, size=(600, 800))

        panel = wx.Panel(self)
        self.panel = panel
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.boxSizer =vbox

        upload_button = wx.Button(panel, label='Upload Image')
        upload_button.Bind(wx.EVT_BUTTON, self.on_upload)
        vbox.Add(upload_button, 0, wx.ALL | wx.CENTER, 5)

        self.image_ctrl = wx.StaticBitmap(panel, bitmap=wx.NullBitmap)
        vbox.Add(self.image_ctrl, 0, wx.ALL | wx.CENTER, 5)
        self.scrolled_window = wx.ScrolledWindow(panel)
        self.imageListSizer = wx.BoxSizer(wx.VERTICAL)
        self.scrolled_window.SetSizer(self.imageListSizer)
        vbox.Add(self.scrolled_window, 1, wx.EXPAND | wx.ALL, 5)  # Add the scrolled window to the main sizer

        panel.SetSizer(vbox)




    def on_upload(self, event):
        with wx.FileDialog(self, "Select PNG file to upload", wildcard="PNG files (*.png)|*.png",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            files = {'query_img': open(pathname, 'rb')}
            data = {'isSVN': 'true', 'resultAsText': 'true'}
            response = requests.post('http://127.0.0.1:5000', files=files,data=data)
            if response.status_code == 200:
                result_text = response.text  # 获取服务器返回的字符串
                print(result_text)  # 打印返回的字符串
                paths = result_text.split('\n')  # 按换行符分割成列表
                self.load_and_show_images(paths)
                # wx.MessageBox("Upload successful", "Success", wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox("Upload failed", "Error", wx.OK | wx.ICON_ERROR)
                
    def load_and_show_images(self, paths):
        # self.imageListSizer.Clear()

        for child in self.scrolled_window.GetChildren():
            child.Destroy()
        for path in paths:
            if path == "":
                continue
            path = "../static/img/svn/" + path
            if path != "" and os.path.exists(path):
                image = wx.Image(path, wx.BITMAP_TYPE_ANY)
                if image.IsOk():
                    bmp = wx.Bitmap(image)
                    static_image = wx.StaticBitmap(self.scrolled_window, -1, bmp, (10, 10))
                    self.imageListSizer.Add(static_image, 0, wx.ALL | wx.CENTER, 5)  # 将图片添加到垂直布局管理器中
                else:
                    print("Invalid image format or path:", path)
            else:
                print("File not found at path:", path)

        self.scrolled_window.SetScrollRate(5, 5)  # Set the scrolling rate
        self.scrolled_window.SetVirtualSize((600, len(paths) * 100))

if __name__ == '__main__':
    app = wx.App()
    frame = ImageUploader(None, "Image Uploader")
    frame.Show()
    app.MainLoop()