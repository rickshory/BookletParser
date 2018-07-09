import wx
import os.path
from pathlib import Path
from PIL import Image, ImageSequence
from PIL import TiffImagePlugin
import copy

class DropTargetForFilesToParse(wx.FileDropTarget):
    def __init__(self, progressArea, msgArea):
        wx.FileDropTarget.__init__(self)
        self.progressArea = progressArea
        self.msgArea = msgArea

    def OnClose(self, event):
        self.Destroy()

    def OnDropFiles(self, x, y, filenames):
        if len(filenames) > 1:
            wx.MessageBox(message="Only do one file at a time",
                          caption='Multiple files',
                          style=wx.OK | wx.ICON_INFORMATION)

            return False

        else:
            self.progressArea.SetValue("")
            self.progressArea.SetInsertionPointEnd()
#            self.progressArea.WriteText("%d file(s) dropped\n" % (len(filenames),))
            curFileName = filenames[0] # get the current file name
            # more validity testing?
            self.progressArea.WriteText(curFileName) # show
            # propose a name for the copy
            newFileName = curFileName[:-4] + ' reading format.tif'
            self.msgArea.SetValue("")
            self.msgArea.SetInsertionPointEnd()
            self.msgArea.WriteText(newFileName)
            return True
        
#        self.progressArea.WriteText("\n%d file(s) dropped at %d,%d:\n" %
#                              (len(filenames), x, y))
#        self.progressArea.WriteText("\n%d file(s) dropped\n" % (len(filenames),))
#        return True
        
class ParserFrame(wx.Frame):
    """
    Frame of the app
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(ParserFrame, self).__init__(*args, **kw)
        self.SetSize((700, 500))
        self.InitUI()
        
    def InitUI(self):
        framePanel = ParseFilesPanel(self, wx.ID_ANY)
        self.Bind(wx.EVT_CLOSE, self.on_close_window)

    def OnClose(self, event):
        self.Destroy()

    def on_close_window(self, event):
        self.Destroy()
        
    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

class ParseFilesPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        self.InitUI()

    def InitUI(self):

        GBSizer = wx.GridBagSizer(0, 0)
        stExplain = """ This utility is for parsing scans of two-page booklets. That is, booklets make of standard 8.5 x 11 sheets, folded in half and stapled along the spine. Each booklet page is then 5.5" wide by 8.5" tall.
 The easy way to scan such a booklet for archiving is to remove the staples and feed the stack of sheets through a scanner. However, viewing the result on-screen is awkward, as the pages that were adjacent in the booklet are now far distant in the scan.
 This utility solves that by taking the multi-page TIF scan, and creating a copy with the half-sheet pages divided out, rotated, and arranged in correct reading order.

 Any existing outut file of the same name will be overwritten."""

        # row 0
        txtExplain = wx.TextCtrl(self, value = stExplain, 
                     style = wx.TE_READONLY|wx.TE_MULTILINE, size=(-1, -1))
        GBSizer.Add(txtExplain, pos=(0, 0), span=(1, 1), flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.BOTTOM, border=10)
        # row 1
        lblDrag = wx.StaticText(self,
                                label="Drag the original scanned booklet TIF to be parsed into the space below")
        GBSizer.Add(lblDrag, pos=(1, 0), span=(1, 1),
            flag=wx.EXPAND|wx.TOP|wx.RIGHT|wx.BOTTOM, 
            border=10)
        # row 2
        textExistingFile = wx.TextCtrl(self, style = wx.TE_MULTILINE)
        self.textExistingFile = textExistingFile
        GBSizer.Add(textExistingFile, pos=(2, 0), span=(1, 1),
            flag=wx.EXPAND|wx.TOP|wx.RIGHT|wx.BOTTOM, 
            border=10)
        # row 3
        lblNewFile = wx.StaticText(self, wx.ID_ANY,
                                   "Filename of copy to be created")
        GBSizer.Add(lblNewFile, pos=(3, 0), span=(1, 1),
            flag=wx.EXPAND|wx.TOP|wx.RIGHT|wx.BOTTOM, 
            border=10)
        # row 4
        textNewFileName = wx.TextCtrl(self, style = wx.TE_MULTILINE)
        self.textNewFileName = textNewFileName
        GBSizer.Add(textNewFileName, pos=(4, 0), span=(1, 1),
            flag=wx.EXPAND|wx.TOP|wx.RIGHT|wx.BOTTOM, 
            border=5)
        
#        dt = DropTargetForFilesToParse(textProgress, textProgMsgs)
#        textProgress.SetDropTarget(dt)

        dt = DropTargetForFilesToParse(textExistingFile, textNewFileName)
        textExistingFile.SetDropTarget(dt)
        # row 5
        # put radio buttons here
        choicesList = ["booklet scan has the first (cover) page in the upper half of the sheet, and page tops are to the left edge of the sheets",
                       "booklet scan has the first (cover) page in the lower half of the sheet, and page tops are to the right edge of the sheets"]
        rb = wx.RadioBox(self, wx.ID_ANY,
                         "Orientation", pos=wx.DefaultPosition,
                         size=wx.DefaultSize,
                         choices=choicesList,
                         majorDimension=2,
                         style=wx.RA_SPECIFY_ROWS)
        self.rb = rb
        GBSizer.Add(rb, pos=(5, 0), span=(1, 1),
            flag=wx.EXPAND|wx.TOP|wx.RIGHT|wx.BOTTOM, 
            border=5)

        # row 6
        btnCreateCopy = wx.Button(self, label="Create Copy", size=(120, 28))
        btnCreateCopy.Bind(wx.EVT_BUTTON, lambda evt: self.makeReaderFile(evt))


        GBSizer.Add(btnCreateCopy, pos=(6, 0), flag=wx.RIGHT|wx.BOTTOM,
                    border=5)
       
        GBSizer.AddGrowableCol(0)
        GBSizer.AddGrowableRow(2)

        self.SetSizerAndFit(GBSizer)
        
    def makeReaderFile(self, event):
#        sel = self.rb.GetSelection()
#        print("RadioBox selection", sel)
#        n = self.textExistingFile.GetNumberOfLines()
#        print("Lines", n)
        existingFileName = self.textExistingFile.GetValue()
        if existingFileName == "":
            print ("no file to work on")

        ck_file = Path(existingFileName)
        if not ck_file.is_file():
            wx.MessageBox(message="Input file does not exist, or is not valid",
                          caption='Bad file',
                          style=wx.OK | wx.ICON_INFORMATION)
            return
        filename, file_extension = os.path.splitext(existingFileName)
        # filename, unused
        if file_extension != '.tif':
            wx.MessageBox(message="Input file must be 'tif' format",
                          caption='Bad file',
                          style=wx.OK | wx.ICON_INFORMATION)

            return        
        print("existingFileName:", existingFileName)
        newCopyFileName = self.textNewFileName.GetValue()
        if newCopyFileName == "":
            print ("no new file to create")
        filename, file_extension = os.path.splitext(newCopyFileName)
        if file_extension != '.tif':
            wx.MessageBox(message="New copy file must be 'tif' format",
                          caption='Bad file',
                          style=wx.OK | wx.ICON_INFORMATION)
            return        
        print("newFileName:", newCopyFileName)
        sel = self.rb.GetSelection()
        if sel == 0:
            print ("Normal, page tops are to left of sheets")
            even_page = 1 # first page is an even page
            rotationAngle = -90
        else:
            print ("Reversed, page tops are to right of sheets")
            even_page = -1 # first page is an odd page
            rotationAngle = 90

        fp = existingFileName
        try:
            im_all = Image.open(fp)
        except IOError as e:
            print ("Unable to open input file")
            wx.MessageBox(message="Can't open input file",
                          caption='Bad file',
                          style=wx.OK | wx.ICON_INFORMATION)
            return
        newfile = newCopyFileName
        try:
            tf = TiffImagePlugin.AppendingTiffWriter(newfile,True)
        except IOError as e:
            print ("Unable to create output file")
            wx.MessageBox(message="Can't create output file",
                          caption='Bad file',
                          style=wx.OK | wx.ICON_INFORMATION)
            return

#        num_orig_pages = im_all.n_frames
        orig_dpi = im_all.info['dpi']
#        print("number of pages to parse", num_orig_pages)
#        num_output_pages = num_orig_pages * 2
        stored_imgs = []

        for i, page in enumerate(ImageSequence.Iterator(im_all)):
            pgwidth, pgheight = page.size

            print("parsing page", i)
            halfheight = pgheight/2
            topbox = (0, 0, pgwidth, halfheight)
            bottombox = (0, halfheight, pgwidth, pgheight)
            im_bottom = page.crop(bottombox).rotate(rotationAngle, 0, 1)
            im_top = page.crop(topbox).rotate(rotationAngle, 0, 1)

            # add the top if an even page, the bottom if an odd page
            # store the other half
            if even_page > 0:
                im_save = im_top
                im_store = im_bottom
            else:
                im_save = im_bottom
                im_store = im_top

##            # temporary diagnostics, to check pixel ranges
##            if i == 0: # save the pages from the first sheet
##                file_pth, file_ext = os.path.splitext(newCopyFileName)
##                im_ck = copy.copy(page)
##                im_ck.save(file_pth + "_ck_sheet" + file_ext)
##                im_bottom.save(file_pth + "_ck_bottom" + file_ext)
##                im_top.save(file_pth + "_ck_top" + file_ext)
                
            saveFrameToTIFBeingBuilt(im_save, tf, orig_dpi)
            stored_imgs.append(copy.copy(im_store))
            even_page = -even_page #toggle even/odd
        # done with the orginal file
        im_all.close()
        # now insert the stored pages
        print("inserting stored half-pages")
        stored_imgs.reverse()
        for im in stored_imgs:
            saveFrameToTIFBeingBuilt(im, tf, orig_dpi)
        tf.close()
        
        print("done")
        wx.MessageBox(message="Done",
              caption='Done',
              style=wx.OK | wx.ICON_INFORMATION)

def saveFrameToTIFBeingBuilt(imgToSave, tfBeingBuilt, DPI):
    # requires imports from the top of this module
    # imgToSave: PIL Image object
    # tfBeingBuilt: open TIF file that is being built, using TiffImagePlugin
    # DPI: dots per inch, tuple of floats, (DBIx, DPIy)
    imgToSave.save(tfBeingBuilt, dpi=(DPI), compression='tiff_lzw',)
    tfBeingBuilt.newFrame()
        
        
if __name__ == '__main__':
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = ParserFrame(None, title='TIF Booklet Parser')
    frm.Show()
    app.MainLoop()
