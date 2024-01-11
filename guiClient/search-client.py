import io
import os

import wx
import requests


class ImageUploader(wx.Frame):
    def __init__(self, parent, title):
        super(ImageUploader, self).__init__(parent, title=title, size=(600, 800))
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
        response = requests.post('http://127.0.0.1:5000', files=files, data=data)
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

    def on_search_clipboard(self, event):
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
        with wx.FileDialog(self, "Select PNG file to upload", wildcard="PNG files (*.png)|*.png",
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
            path = "../static/img/svn/" + path
            if path != "" and os.path.exists(path):
                image = wx.Image(path, wx.BITMAP_TYPE_ANY)
                if image.IsOk():
                    size_desc = "大小:" + str(image.GetWidth()) + "X" + str(image.GetHeight())
                    image = self.clamp_image_size(image, 300)
                    bmp = wx.Bitmap(image)
                    static_image = wx.StaticBitmap(self.scrolled_window, -1, bmp, (10, 10))
                    item_sizer = wx.BoxSizer(wx.HORIZONTAL)
                    vertical_sizer = wx.BoxSizer(wx.VERTICAL)
                    item_sizer.Add(static_image, 0, wx.ALL | wx.LEFT, 5)
                    item_sizer.Add(vertical_sizer, 0, wx.ALL | wx.LEFT, 5)
                    vertical_sizer.Add(wx.StaticText(self.scrolled_window, label=path), 0, wx.ALL | wx.Right, 5)
                    vertical_sizer.Add(wx.StaticText(self.scrolled_window, label=size_desc), 0, wx.ALL | wx.Right, 5)
                    self.imageListSizer.Add(item_sizer, 0, wx.ALL | wx.LEFT, 5)  # 将图片添加到垂直布局管理器中
                else:
                    print("Invalid image format or path:", path)
            else:
                print("File not found at path:", path)

        self.scrolled_window.SetScrollRate(5, 5)  # Set the scrolling rate
        self.scrolled_window.SetVirtualSize((600, len(paths) * 100))
        self.scrolled_window.Scroll(0, 0)


if __name__ == '__main__':
    app = wx.App()
    frame = ImageUploader(None, "ImageSearcher")
    frame.Show()
    app.MainLoop()
