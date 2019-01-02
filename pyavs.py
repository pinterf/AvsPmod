# AvsP - an AviSynth editor
# GPo mod m14 up
#
# Copyright 2007 Peter Jang <http://www.avisynth.org/qwerpoi>
#           2010-2017 the AvsPmod authors <https://github.com/avspmod/avspmod>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA, or visit
#  http://www.gnu.org/copyleft/gpl.html .

# pyavs - AVI functions via AviSynth in Python
# Drawing uses VFW on Windows and generical wxPython support on other platforms
#
# Dependencies:
#     Python (tested on v2.6 and v2.7)
#     wxPython (for *nix, tested on v2.8 and v2.9)
#     cffi and its dependencies (only for x86-64, tested on v0.9.2)
#         pycparser
#         Visual C++
#     avisynth_c.h (only for x86-64, interface 5, or at least 3 + colorspaces
#                   from 5, tested with the header used by x264)
# Scripts:
#     avisynth.py (Python AviSynth/AvxSynth wrapper, only for x86-32)
#     avisynth_cffi.py (Python AviSynth wrapper, only for x86-64)

import sys
import os
import ctypes
import re

x86_64 = sys.maxsize > 2**32
if x86_64:
    import avisynth_cffi as avisynth
else:
    import avisynth
import global_vars

try: _
except NameError:
    def _(s): return s

"""
########## Alternative get colorspace ##########
################################################
# GPo, avs plus (interface 6) pixel_type x32 compatible, x64 bit shift is not the same.
class avs_plus():
    CS_YUVA = 1<<27
    CS_BGR = 1<<28
    CS_YUV = 1<<29
    CS_INTERLEAVED = 1<<30
    CS_PLANAR = 1<<31

    CS_Shift_Sub_Width   =  0
    CS_Shift_Sub_Height  =  8
    CS_Shift_Sample_Bits = 16

    CS_Sub_Width_Mask    = 7 << CS_Shift_Sub_Width
    CS_Sub_Width_1       = 3 << CS_Shift_Sub_Width # YV24
    CS_Sub_Width_2       = 0 << CS_Shift_Sub_Width # YV12 I420 YV16
    CS_Sub_Width_4       = 1 << CS_Shift_Sub_Width # YUV9 YV411

    CS_VPlaneFirst       = 1 << 3 # YV12 YV16 YV24 YV411 YUV9
    CS_UPlaneFirst       = 1 << 4 # I420

    CS_Sub_Height_Mask   = 7 << CS_Shift_Sub_Height
    CS_Sub_Height_1      = 3 << CS_Shift_Sub_Height # YV16 YV24 YV411
    CS_Sub_Height_2      = 0 << CS_Shift_Sub_Height # YV12 I420
    CS_Sub_Height_4      = 1 << CS_Shift_Sub_Height # YUV9

    CS_Sample_Bits_Mask  = 7 << CS_Shift_Sample_Bits
    CS_Sample_Bits_8     = 0 << CS_Shift_Sample_Bits
    CS_Sample_Bits_10    = 5 << CS_Shift_Sample_Bits
    CS_Sample_Bits_12    = 6 << CS_Shift_Sample_Bits
    CS_Sample_Bits_14    = 7 << CS_Shift_Sample_Bits
    CS_Sample_Bits_16    = 1 << CS_Shift_Sample_Bits
    CS_Sample_Bits_32    = 2 << CS_Shift_Sample_Bits

    CS_PLANAR_MASK       = CS_PLANAR | CS_INTERLEAVED | CS_YUV | CS_BGR | CS_YUVA | \
                           CS_Sample_Bits_Mask | CS_Sub_Height_Mask | CS_Sub_Width_Mask
    CS_PLANAR_FILTER     = ~( CS_VPlaneFirst | CS_UPlaneFirst )

    CS_RGB_TYPE  = 1 << 0
    CS_RGBA_TYPE = 1 << 1

    # Specific colorformats
    CS_UNKNOWN = 0

    CS_BGR24 = CS_RGB_TYPE  | CS_BGR | CS_INTERLEAVED
    CS_BGR32 = CS_RGBA_TYPE | CS_BGR | CS_INTERLEAVED
    CS_YUY2  = 1<<2 | CS_YUV | CS_INTERLEAVED
    #  CS_YV12  = 1<<3  Reserved
    #  CS_I420  = 1<<4  Reserved
    CS_RAW32 = 1<<5 | CS_INTERLEAVED

    #  YV12 must be 0xA000008 2.5 Baked API will see all new planar as YV12
    #  I420 must be 0xA000010

    CS_GENERIC_YUV420  = CS_PLANAR | CS_YUV | CS_VPlaneFirst | CS_Sub_Height_2 | CS_Sub_Width_2  # 4:2:0 planar
    CS_GENERIC_YUV422  = CS_PLANAR | CS_YUV | CS_VPlaneFirst | CS_Sub_Height_1 | CS_Sub_Width_2  # 4:2:2 planar
    CS_GENERIC_YUV444  = CS_PLANAR | CS_YUV | CS_VPlaneFirst | CS_Sub_Height_1 | CS_Sub_Width_1  # 4:4:4 planar
    CS_GENERIC_Y       = CS_PLANAR | CS_INTERLEAVED | CS_YUV                                     # Y only (4:0:0)
    CS_GENERIC_RGBP    = CS_PLANAR | CS_BGR | CS_RGB_TYPE                                        # planar RGB. Though name is RGB but plane order GBR
    CS_GENERIC_RGBAP   = CS_PLANAR | CS_BGR | CS_RGBA_TYPE                                       # planar RGBA
    CS_GENERIC_YUVA420 = CS_PLANAR | CS_YUVA | CS_VPlaneFirst | CS_Sub_Height_2 | CS_Sub_Width_2 # 4:2:0:A planar
    CS_GENERIC_YUVA422 = CS_PLANAR | CS_YUVA | CS_VPlaneFirst | CS_Sub_Height_1 | CS_Sub_Width_2 # 4:2:2:A planar
    CS_GENERIC_YUVA444 = CS_PLANAR | CS_YUVA | CS_VPlaneFirst | CS_Sub_Height_1 | CS_Sub_Width_1 # 4:4:4:A planar

    CS_YV24  = CS_GENERIC_YUV444 | CS_Sample_Bits_8  # YVU 4:4:4 planar
    CS_YV16  = CS_GENERIC_YUV422 | CS_Sample_Bits_8  # YVU 4:2:2 planar
    CS_YV12  = CS_GENERIC_YUV420 | CS_Sample_Bits_8  # YVU 4:2:0 planar
    CS_I420  = CS_PLANAR | CS_YUV | CS_Sample_Bits_8 | CS_UPlaneFirst | CS_Sub_Height_2 | CS_Sub_Width_2  # YUV 4:2:0 planar
    CS_IYUV  = CS_I420
    CS_YUV9  = CS_PLANAR | CS_YUV | CS_Sample_Bits_8 | CS_VPlaneFirst | CS_Sub_Height_4 | CS_Sub_Width_4  # YUV 4:1:0 planar
    CS_YV411 = CS_PLANAR | CS_YUV | CS_Sample_Bits_8 | CS_VPlaneFirst | CS_Sub_Height_1 | CS_Sub_Width_4  # YUV 4:1:1 planar

    CS_Y8    = CS_GENERIC_Y | CS_Sample_Bits_8                                                            # Y   4:0:0 planar

    #-------------------------
    # AVS16: new planar constants go live! Experimental PF 160613
    # 10-12-14 bit + planar RGB + BRG48/64 160725

    CS_YUV444P10 = CS_GENERIC_YUV444 | CS_Sample_Bits_10 # YUV 4:4:4 10bit samples
    CS_YUV422P10 = CS_GENERIC_YUV422 | CS_Sample_Bits_10 # YUV 4:2:2 10bit samples
    CS_YUV420P10 = CS_GENERIC_YUV420 | CS_Sample_Bits_10 # YUV 4:2:0 10bit samples
    CS_Y10 = CS_GENERIC_Y | CS_Sample_Bits_10            # Y   4:0:0 10bit samples

    CS_YUV444P12 = CS_GENERIC_YUV444 | CS_Sample_Bits_12 # YUV 4:4:4 12bit samples
    CS_YUV422P12 = CS_GENERIC_YUV422 | CS_Sample_Bits_12 # YUV 4:2:2 12bit samples
    CS_YUV420P12 = CS_GENERIC_YUV420 | CS_Sample_Bits_12 # YUV 4:2:0 12bit samples
    CS_Y12 = CS_GENERIC_Y | CS_Sample_Bits_12            # Y   4:0:0 12bit samples

    CS_YUV444P14 = CS_GENERIC_YUV444 | CS_Sample_Bits_14 # YUV 4:4:4 14bit samples
    CS_YUV422P14 = CS_GENERIC_YUV422 | CS_Sample_Bits_14 # YUV 4:2:2 14bit samples
    CS_YUV420P14 = CS_GENERIC_YUV420 | CS_Sample_Bits_14 # YUV 4:2:0 14bit samples
    CS_Y14 = CS_GENERIC_Y | CS_Sample_Bits_14            # Y   4:0:0 14bit samples

    CS_YUV444P16 = CS_GENERIC_YUV444 | CS_Sample_Bits_16 # YUV 4:4:4 16bit samples
    CS_YUV422P16 = CS_GENERIC_YUV422 | CS_Sample_Bits_16 # YUV 4:2:2 16bit samples
    CS_YUV420P16 = CS_GENERIC_YUV420 | CS_Sample_Bits_16 # YUV 4:2:0 16bit samples
    CS_Y16 = CS_GENERIC_Y | CS_Sample_Bits_16            # Y   4:0:0 16bit samples

    # 32 bit samples (float)
    CS_YUV444PS = CS_GENERIC_YUV444 | CS_Sample_Bits_32  # YUV 4:4:4 32bit samples
    CS_YUV422PS = CS_GENERIC_YUV422 | CS_Sample_Bits_32  # YUV 4:2:2 32bit samples
    CS_YUV420PS = CS_GENERIC_YUV420 | CS_Sample_Bits_32  # YUV 4:2:0 32bit samples
    CS_Y32 = CS_GENERIC_Y | CS_Sample_Bits_32            # Y   4:0:0 32bit samples

    # RGB packed
    CS_BGR48 = CS_RGB_TYPE  | CS_BGR | CS_INTERLEAVED | CS_Sample_Bits_16 # BGR 3x16 bit
    CS_BGR64 = CS_RGBA_TYPE | CS_BGR | CS_INTERLEAVED | CS_Sample_Bits_16 # BGR 4x16 bit
    # no packed 32 bit (float) support for these legacy types

    # RGB planar
    CS_RGBP   = CS_GENERIC_RGBP | CS_Sample_Bits_8  # Planar RGB 8 bit samples
    CS_RGBP10 = CS_GENERIC_RGBP | CS_Sample_Bits_10 # Planar RGB 10bit samples
    CS_RGBP12 = CS_GENERIC_RGBP | CS_Sample_Bits_12 # Planar RGB 12bit samples
    CS_RGBP14 = CS_GENERIC_RGBP | CS_Sample_Bits_14 # Planar RGB 14bit samples
    CS_RGBP16 = CS_GENERIC_RGBP | CS_Sample_Bits_16 # Planar RGB 16bit samples
    CS_RGBPS  = CS_GENERIC_RGBP | CS_Sample_Bits_32 # Planar RGB 32bit samples

    # RGBA planar
    CS_RGBAP   = CS_GENERIC_RGBAP | CS_Sample_Bits_8  # Planar RGBA 8 bit samples
    CS_RGBAP10 = CS_GENERIC_RGBAP | CS_Sample_Bits_10 # Planar RGBA 10bit samples
    CS_RGBAP12 = CS_GENERIC_RGBAP | CS_Sample_Bits_12 # Planar RGBA 12bit samples
    CS_RGBAP14 = CS_GENERIC_RGBAP | CS_Sample_Bits_14 # Planar RGBA 14bit samples
    CS_RGBAP16 = CS_GENERIC_RGBAP | CS_Sample_Bits_16 # Planar RGBA 16bit samples
    CS_RGBAPS  = CS_GENERIC_RGBAP | CS_Sample_Bits_32 # Planar RGBA 32bit samples

    # Planar YUVA
    CS_YUVA444    = CS_GENERIC_YUVA444 | CS_Sample_Bits_8  # YUVA 4:4:4 8bit samples
    CS_YUVA422    = CS_GENERIC_YUVA422 | CS_Sample_Bits_8  # YUVA 4:2:2 8bit samples
    CS_YUVA420    = CS_GENERIC_YUVA420 | CS_Sample_Bits_8  # YUVA 4:2:0 8bit samples

    CS_YUVA444P10 = CS_GENERIC_YUVA444 | CS_Sample_Bits_10 # YUVA 4:4:4 10bit samples
    CS_YUVA422P10 = CS_GENERIC_YUVA422 | CS_Sample_Bits_10 # YUVA 4:2:2 10bit samples
    CS_YUVA420P10 = CS_GENERIC_YUVA420 | CS_Sample_Bits_10 # YUVA 4:2:0 10bit samples

    CS_YUVA444P12 = CS_GENERIC_YUVA444 | CS_Sample_Bits_12 # YUVA 4:4:4 12bit samples
    CS_YUVA422P12 = CS_GENERIC_YUVA422 | CS_Sample_Bits_12 # YUVA 4:2:2 12bit samples
    CS_YUVA420P12 = CS_GENERIC_YUVA420 | CS_Sample_Bits_12 # YUVA 4:2:0 12bit samples

    CS_YUVA444P14 = CS_GENERIC_YUVA444 | CS_Sample_Bits_14 # YUVA 4:4:4 14bit samples
    CS_YUVA422P14 = CS_GENERIC_YUVA422 | CS_Sample_Bits_14 # YUVA 4:2:2 14bit samples
    CS_YUVA420P14 = CS_GENERIC_YUVA420 | CS_Sample_Bits_14 # YUVA 4:2:0 14bit samples

    CS_YUVA444P16 = CS_GENERIC_YUVA444 | CS_Sample_Bits_16 # YUVA 4:4:4 16bit samples
    CS_YUVA422P16 = CS_GENERIC_YUVA422 | CS_Sample_Bits_16 # YUVA 4:2:2 16bit samples
    CS_YUVA420P16 = CS_GENERIC_YUVA420 | CS_Sample_Bits_16 # YUVA 4:2:0 16bit samples

    CS_YUVA444PS  = CS_GENERIC_YUVA444 | CS_Sample_Bits_32  # YUVA 4:4:4 32bit samples
    CS_YUVA422PS  = CS_GENERIC_YUVA422 | CS_Sample_Bits_32  # YUVA 4:2:2 32bit samples
    CS_YUVA420PS  = CS_GENERIC_YUVA420 | CS_Sample_Bits_32  # YUVA 4:2:0 32bit samples

def avs_plus_get_colorspace_name(pixel_type):
    if x86_64:
        # can't compile x64 AvsPmod, workaround
        avs_ColorspaceDict = {
            -1610284277 : "YUV444P10",
            -1610218741 : "YUV444P12",
            -1610153205 : "YUV444P14",
            -1610546421 : "YUV444P16",
            -1610480885 : "YUV444PS",
            -1610284280 : "YUV422P10",
            -1610218744 : "YUV422P12",
            -1610153208 : "YUV422P14",
            -1610546424 : "YUV422P16",
            -1610480888 : "YUV422PS",
            -1610285048 : "YUV420P10",
            -1610219512 : "YUV420P12",
            -1610153976 : "YUV420P14",
            -1610547192 : "YUV420P16",
            -1610481656 : "YUV420PS",
            -536543232 : "Y10",
            -536477696 : "Y12",
            -536412160 : "Y14",
            -536805376 : "Y16",
            -536739840 : "Y32",
            1342177281 : "RGB24",
            1342177282 : "RGB32",
            1342242817 : "RGB48",
            1342242818 : "RGB64"
        }
    else:
    	avs_ColorspaceDict = {
    		avs_plus.CS_BGR24: "RGB24",
    		avs_plus.CS_BGR32: "RGB32",
    		avs_plus.CS_YUY2 : "YUY2",
    		avs_plus.CS_YV24 : "YV24",
    		avs_plus.CS_YV16 : "YV16",
    		avs_plus.CS_YV12 : "YV12",
    		avs_plus.CS_I420 : "YV12",
    		avs_plus.CS_YUV9 : "YUV9",
    		avs_plus.CS_YV411: "YV411",
    		avs_plus.CS_Y8   : "Y8",
    		avs_plus.CS_YUV420P10: "YUV420P10",
    		avs_plus.CS_YUV422P10: "YUV422P10",
    		avs_plus.CS_YUV444P10: "YUV444P10",
    		avs_plus.CS_Y10      : "Y10",
    		avs_plus.CS_YUV420P12: "YUV420P12",
    		avs_plus.CS_YUV422P12: "YUV422P12",
    		avs_plus.CS_YUV444P12: "YUV444P12",
    		avs_plus.CS_Y12      : "Y12",
    		avs_plus.CS_YUV420P14: "YUV420P14",
    		avs_plus.CS_YUV422P14: "YUV422P14",
    		avs_plus.CS_YUV444P14: "YUV444P14",
    		avs_plus.CS_Y14      : "Y14",
    		avs_plus.CS_YUV420P16: "YUV420P16",
    		avs_plus.CS_YUV422P16: "YUV422P16",
    		avs_plus.CS_YUV444P16: "YUV444P16",
    		avs_plus.CS_Y16      : "Y16",
    		avs_plus.CS_YUV420PS : "YUV420PS",
    		avs_plus.CS_YUV422PS : "YUV422PS",
    		avs_plus.CS_YUV444PS : "YUV444PS",
    		avs_plus.CS_Y32      : "Y32",
    		avs_plus.CS_BGR48    : "RGB48",
    		avs_plus.CS_BGR64    : "RGB64",
    		avs_plus.CS_RGBP     : "RGBP",
    		avs_plus.CS_RGBP10   : "RGBP10",
    		avs_plus.CS_RGBP12   : "RGBP12",
    		avs_plus.CS_RGBP14   : "RGBP14",
    		avs_plus.CS_RGBP16   : "RGBP16",
    		avs_plus.CS_RGBPS    : "RGBPS",
    		avs_plus.CS_YUVA420  : "YUVA420",
    		avs_plus.CS_YUVA422  : "YUVA422",
    		avs_plus.CS_YUVA444  : "YUVA444",
    		avs_plus.CS_YUVA420P10: "YUVA420P10",
    		avs_plus.CS_YUVA422P10: "YUVA422P10",
    		avs_plus.CS_YUVA444P10: "YUVA444P10",
    		avs_plus.CS_YUVA420P12: "YUVA420P12",
    		avs_plus.CS_YUVA422P12: "YUVA422P12",
    		avs_plus.CS_YUVA444P12: "YUVA444P12",
    		avs_plus.CS_YUVA420P14: "YUVA420P14",
    		avs_plus.CS_YUVA422P14: "YUVA422P14",
    		avs_plus.CS_YUVA444P14: "YUVA444P14",
    		avs_plus.CS_YUVA420P16: "YUVA420P16",
    		avs_plus.CS_YUVA422P16: "YUVA422P16",
    		avs_plus.CS_YUVA444P16: "YUVA444P16",
    		avs_plus.CS_YUVA420PS : "YUVA420PS",
    		avs_plus.CS_YUVA422PS : "YUVA422PS",
    		avs_plus.CS_YUVA444PS : "YUVA444PS",
    		avs_plus.CS_RGBAP     : "RGBAP",
    		avs_plus.CS_RGBAP10   : "RGBAP10",
    		avs_plus.CS_RGBAP12   : "RGBAP12",
    		avs_plus.CS_RGBAP14   : "RGBAP14",
    		avs_plus.CS_RGBAP16   : "RGBAP16",
    		avs_plus.CS_RGBAPS    : "RGBAPS"
    	}

    if pixel_type in avs_ColorspaceDict:
        return avs_ColorspaceDict[pixel_type]
    return ''
"""

class AvsClipBase:

    def __init__(self, script, filename='', workdir='', env=None, fitHeight=None,
                 fitWidth=None, oldFramecount=240, display_clip=True, reorder_rgb=False,
                 matrix=['auto', 'tv'], interlaced=False, swapuv=False, bit_depth=None):
        # Internal variables
        self.initialized = False
        self.name = filename
        self.error_message = None
        self.current_frame = -1
        self.pBits = None
        self.display_clip = None
        self.ptrY = self.ptrU = self.ptrV = None
        # Avisynth script properties
        self.Width = -1
        self.Height = -1
        self.WidthSubsampling = -1
        self.HeightSubsampling = -1
        self.Framecount = -1
        self.Framerate = -1.0
        self.FramerateNumerator = -1
        self.FramerateDenominator = -1
        self.Audiorate = -1.0
        self.Audiolength = -1
        #~ self.AudiolengthF = None
        self.Audiochannels = -1
        self.Audiobits = -1
        self.IsAudioFloat = None
        self.IsAudioInt = None
        self.IsRGB = None
        self.IsRGB24 = None
        self.IsRGB32 = None
        self.IsYUV = None
        self.IsYUY2 = None
        self.IsYV24 = None
        self.IsYV16 = None
        self.IsYV12 = None
        self.IsYV411 = None
        self.IsY8 = None
        self.avsplus_colorspace = False
        self.IsPlanar = None
        self.IsInterleaved = None
        self.IsFieldBased = None
        self.IsFrameBased = None
        self.GetParity  = None
        self.HasAudio = None
        self.HasVideo = None
        self.Colorspace = None
        self.ffms_info_cache = {}

        # Create the Avisynth script clip
        if env is not None:
            if isinstance(env, avisynth.AVS_ScriptEnvironment):
                self.env = env
            else:
                raise TypeError("env must be a PIScriptEnvironment or None")
        else:
            if isinstance(script, avisynth.AVS_Clip):
                raise ValueError("env must be defined when providing a clip")
            try:
                self.env = avisynth.AVS_ScriptEnvironment(3)
            except OSError:
                return
            if hasattr(self.env, 'get_error'):
                self.error_message = self.env.get_error()
                if self.error_message: return
        if isinstance(script, avisynth.AVS_Clip):
            self.clip = script
        else:
            # vpy hack, remove when VapourSynth is supported
            if os.name == 'nt' and filename.endswith('.vpy'):
                if self.env.function_exists('AutoloadPlugins'): # AviSynth+
                    try:
                        self.env.invoke('AutoloadPlugins')
                    except avisynth.AvisynthError as err:
                        self.Framecount = oldFramecount
                        if not self.CreateErrorClip(err):
                            return
                if self.env.function_exists('VSImport'):
                    script = ur'VSImport("{0}", stacked=true)'.format(filename)
                else:
                    script = ur'AviSource("{0}")'.format(filename)
            scriptdirname, scriptbasename = os.path.split(filename)
            curdir = os.getcwdu()
            workdir = os.path.isdir(workdir) and workdir or scriptdirname
            if os.path.isdir(workdir):
                self.env.set_working_dir(workdir)
            self.env.set_global_var("$ScriptFile$", scriptbasename)
            self.env.set_global_var("$ScriptName$", filename)
            self.env.set_global_var("$ScriptDir$", scriptdirname + os.path.sep)
            try:
                self.clip = self.env.invoke('Eval', [script, filename])
                if not isinstance(self.clip, avisynth.AVS_Clip):
                    raise avisynth.AvisynthError("Not a clip")
            except avisynth.AvisynthError as err:
                self.Framecount = oldFramecount
                if not self.CreateErrorClip(err):
                    return
            finally:
                os.chdir(curdir)
            try:
                if not isinstance(self.env.get_var("last"), avisynth.AVS_Clip):
                    self.env.set_var("last", self.clip)
            except avisynth.AvisynthError as err:
                if str(err) != 'NotFound':
                    raise
                self.env.set_var("last", self.clip)
            self.env.set_var("avsp_raw_clip", self.clip)
            if self.env.function_exists('AutoloadPlugins'): # AviSynth+
                try:
                    self.env.invoke('AutoloadPlugins')
                except avisynth.AvisynthError as err:
                    self.Framecount = oldFramecount
                    if not self.CreateErrorClip(err):
                        return

        # Set the video properties
        self.vi = self.clip.get_video_info()
        self.HasVideo = self.vi.has_video()
        if not self.HasVideo:
            self.clip = None
            errText = 'MessageClip("No video")'
            try:
                self.clip = self.env.invoke('Eval', errText)
                if not isinstance(self.clip, avisynth.AVS_Clip):
                    raise avisynth.AvisynthError("Not a clip")
            except avisynth.AvisynthError as err:
                return
            try:
                if not isinstance(self.env.get_var('last'), avisynth.AVS_Clip):
                    self.env.set_var('last', self.clip)
            except avisynth.AvisynthError as err:
                if str(err) != 'NotFound':
                    raise
                self.env.set_var('last', self.clip)
            self.vi=self.clip.get_video_info()
            self.HasVideo = self.vi.has_video()
        self.Framecount = self.vi.num_frames
        self.Width = self.vi.width
        self.Height = self.vi.height
        if self.vi.is_yuv() and not self.vi.is_y8():
            self.WidthSubsampling = self.vi.get_plane_width_subsampling(avisynth.avs.AVS_PLANAR_U)
            self.HeightSubsampling = self.vi.get_plane_height_subsampling(avisynth.avs.AVS_PLANAR_U)
        self.DisplayWidth, self.DisplayHeight = self.Width, self.Height
        self.FramerateNumerator = self.vi.fps_numerator
        self.FramerateDenominator = self.vi.fps_denominator
        try:
            self.Framerate = self.vi.fps_numerator / float(self.vi.fps_denominator)
        except ZeroDivisionError:
            pass
        self.sample_type_dict = {
            avisynth.avs.AVS_SAMPLE_INT8: 8,
            avisynth.avs.AVS_SAMPLE_INT16: 16,
            avisynth.avs.AVS_SAMPLE_INT24: 24,
            avisynth.avs.AVS_SAMPLE_INT32: 32,
            avisynth.avs.AVS_SAMPLE_FLOAT: 32,
        }
        self.Audiorate = self.vi.audio_samples_per_second
        self.Audiolength = self.vi.num_audio_samples
        self.Audiochannels = self.vi.nchannels
        self.Audiobits = self.sample_type_dict.get(self.vi.sample_type, 0)
        self.IsAudioFloat = self.vi.sample_type == avisynth.avs.AVS_SAMPLE_FLOAT
        self.IsAudioInt = not self.IsAudioFloat
        self.IsRGB = self.vi.is_rgb()
        #self.IsRGB24 = self.vi.is_rgb24()  # GPo, needed for Alternative
        #self.IsRGB32 = self.vi.is_rgb32()  # GPo, needed for Alternative
        self.IsYUV = self.vi.is_yuv()
        self.IsYUY2 = self.vi.is_yuy2()
        self.IsYV24 = self.vi.is_yv24()
        self.IsYV16 = self.vi.is_yv16()
        self.IsYV12 = self.vi.is_yv12()
        self.IsYV411 = self.vi.is_yv411()
        self.IsY8 = self.vi.is_y8()

        # Possible even for classic avs:
        '''
        self.IsRGB48 = self.vi.isRGB48
        self.IsRGB64 = self.vi.isRGB64
        self.Is444 = self.vi.is_444() # use this one instead of IsYV24
        self.Is422 = self.vi.is_422() # use this one instead of IsYV16
        self.Is420 = self.vi.is_420() # use this one instead of IsYV12
        self.IsY = self.vi.is_y() # use this one instead of IsY8
        self.num_components = self.vi.num_components() # 1-4
        self.component_size = self.vi.component_size() # 1, 2, 4 (in bytes)
        self.bits_per_component = self.vi.bits_per_component() # 8,10,12,14,16,32
        '''

        # GPo, avs plus get colorspace
        cName = ''
        if self.env.function_exists('PixelType') and self.clip:
            cName = self.env.invoke("PixelType", self.clip)
        if cName:
            # RGB workaround 32,64 bit and 24,48 bit
            self.IsRGB24 = cName == 'RGB24'
            self.IsRGB32 = cName == 'RGB32'
            self.avsplus_colorspace = True
            self.Colorspace = (cName*self.avsplus_colorspace)
        else:
            self.IsRGB24 = self.vi.is_rgb24()
            self.IsRGB32 = self.vi.is_rgb32()
            self.Colorspace = ('RGB24'*self.IsRGB24 + 'RGB32'*self.IsRGB32 + 'YUY2'*self.IsYUY2 + 'YV12'*self.IsYV12 +
                               'YV24'*self.IsYV24 + 'YV16'*self.IsYV16 + 'YV411'*self.IsYV411 + 'Y8'*self.IsY8
                               )

        """
        # Alternative get colorspace, not full x64 compatible
        # check if found
        if int(self.IsYUY2 + self.IsYV24 + self.IsYV16 +
               self.IsYV12 + self.IsYV411 + self.IsY8) <= 0:
            # if not get it from avs_plus
            cName = avs_plus_get_colorspace_name(self.vi.pixel_type)
            self.avsplus_colorspace = bool(cName)
            # RGB24,32 workaround
            cName = cName.strip('RGB32').strip('RGB24')
            if self.IsRGB32 and cName == 'RGB64':
                self.IsRGB32 = False
            elif self.IsRGB24 and cName == 'RGB48':
               self.IsRGB24 = False
        else:
            cName= 'plus'
        # for test only print '%i' % long(self.vi.pixel_type)
        self.Colorspace = ('RGB24'*self.IsRGB24 + 'RGB32'*self.IsRGB32 + 'YUY2'*self.IsYUY2 + 'YV12'*self.IsYV12 +
                           'YV24'*self.IsYV24 + 'YV16'*self.IsYV16 + 'YV411'*self.IsYV411 + 'Y8'*self.IsY8 +
                           cName*self.avsplus_colorspace
                           )
        """

        self.IsPlanar = self.vi.is_planar()
#        self.IsInterleaved = self.vi.is_interleaved()
        self.IsFieldBased = self.vi.is_field_based()
        self.IsFrameBased = not self.IsFieldBased
        self.GetParity = self.clip.get_parity(0) #self.vi.image_type
        self.HasAudio = self.vi.has_audio()

        self.interlaced = interlaced
        if display_clip and not self.CreateDisplayClip(matrix, interlaced, swapuv, bit_depth):
            return
        if self.IsRGB and reorder_rgb:
            self.clip = self.BGR2RGB(self.clip)
        self.initialized = True
        if __debug__:
            print(u"AviSynth clip created successfully: '{0}'".format(self.name))

    def __del__(self):
        if self.initialized:
            self.display_frame = None
            self.src_frame = None
            self.display_clip = None
            self.env.set_var("avsp_raw_clip", None)
            self.clip = None
            if __debug__:
                print(u"Deleting allocated video memory for '{0}'".format(self.name))

    def CreateErrorClip(self, err='', display_clip_error=False):
        fontFace, fontSize, fontColor = global_vars.options['errormessagefont'][:3]   # GPo fontColor
        if fontColor == '':
            fontColor = '$FF0000'

        if display_clip_error:
            if not err:
                err = _('Error trying to display the clip')
                if self.bit_depth:
                    err += '\n' + _('Is bit-depth set correctly?')
        else:
            err = str(err)
            self.error_message = err
        lineList = []
        yLine = 0
        nChars = 0
        for errLine in err.split('\n'):
            lineList.append('Subtitle("""%s""",y=%i,font="%s",size=%i,text_color=%s,align=8)' %
                (errLine, yLine, fontFace.encode(sys.getfilesystemencoding()), fontSize, fontColor))   # GPo fontColor
            yLine += fontSize
            nChars = max(nChars, len(errLine))
        eLength = self.Framecount
        eWidth = nChars * fontSize / 2
        eHeight = yLine + fontSize / 4
        firstLine = 'BlankClip(length=%(eLength)i,width=%(eWidth)i,height=%(eHeight)i)' % locals()
        errText = firstLine + '.'.join(lineList)
        try:
            clip = self.env.invoke('Eval', errText)
            if not isinstance(clip, avisynth.AVS_Clip):
                raise avisynth.AvisynthError("Not a clip")
            if display_clip_error:
                self.display_clip = clip
                vi = self.display_clip.get_video_info()
                self.DisplayWidth = vi.width
                self.DisplayHeight = vi.height + 10  # GPo + 10
            else:
                self.clip = clip
        except avisynth.AvisynthError as err:
            return False
        return True

    def CreateDisplayClip(self, matrix=['auto', 'tv'], interlaced=None, swapuv=False, bit_depth=None):
        self.current_frame = -1
        self.display_clip = self.clip
        self.RGB48 = False
        self.bit_depth = bit_depth
        if bit_depth:
            try:
                if bit_depth == 'rgb48': # TODO
                    if self.IsYV12:
                        self.RGB48 = True
                        self.DisplayWidth /= 2
                        self.DisplayHeight /= 2
                        return True
                elif self.IsYV12 or self.IsYV24 or self.IsY8:
                    if bit_depth == 's16':
                        args = [self.display_clip, 0, 0, 0, self.Height / 2]
                        self.display_clip = self.env.invoke('Crop', args)
                    elif bit_depth == 's10':
                        if self.env.function_exists('mt_lutxy'):
                            args = (
                            'avsp_raw_clip\n'
                            'msb = Crop(0, 0, Width(), Height() / 2)\n'
                            'lsb = Crop(0, Height() / 2, Width(), Height() / 2)\n'
                            'mt_lutxy(msb, lsb, "x 8 << y + 2 >>", chroma="process")')
                            self.display_clip = self.env.invoke('Eval', args)
                    elif bit_depth == 'i16':
                        args = ('avsp_raw_clip.AssumeBFF().TurnLeft().SeparateFields().'
                                'TurnRight().AssumeFrameBased().SelectOdd()')
                        self.display_clip = self.env.invoke('Eval', args)
                    elif bit_depth == 'i10':
                        if self.env.function_exists('mt_lutxy'):
                            args = (
                            'avsp_raw_clip.AssumeBFF().TurnLeft().SeparateFields().TurnRight().AssumeFrameBased()\n'
                            'mt_lutxy(SelectOdd(), SelectEven(), "x 8 << y + 2 >>", chroma="process")')
                            self.display_clip = self.env.invoke('Eval', args)
                    if not isinstance(self.display_clip, avisynth.AVS_Clip):
                        raise avisynth.AvisynthError("Not a clip")
                    vi = self.display_clip.get_video_info()
                    self.DisplayWidth = vi.width
                    self.DisplayHeight = vi.height
            except avisynth.AvisynthError as err:
                return self.CreateErrorClip(display_clip_error=True)
        if isinstance(matrix, basestring):
            self.matrix = matrix
        else:
            matrix = matrix[:]
            if matrix[0] == 'auto':
                if self.DisplayWidth > 1024 or self.DisplayHeight > 576:
                    matrix[0] = '709'
                else:
                    matrix[0] = '601'
            matrix[1] = 'Rec' if (matrix[1] == 'tv' or matrix[0] == '2020') else 'PC.'  # GPo, Rec2020
            self.matrix = matrix[1] + matrix[0]
        if interlaced is not None:
            self.interlaced = interlaced
        if swapuv and self.IsYUV and not self.IsY8:
            try:
                self.display_clip = self.env.invoke('SwapUV', self.display_clip)
            except avisynth.AvisynthError as err:
                return self.CreateErrorClip(display_clip_error=True)
        vi = self.display_clip.get_video_info()
        self.DisplayWidth = vi.width
        self.DisplayHeight = vi.height
        if not self._ConvertToRGB():
            return self.CreateErrorClip(display_clip_error=True)
        return True

    def _ConvertToRGB(self):
        '''Convert to RGB for display. Return True if successful'''
        pass

    def _GetFrame(self, frame):
        if self.initialized:
            if self.current_frame == frame:
                return True
            if frame < 0:
                frame = 0
            if frame >= self.Framecount:
                frame = self.Framecount - 1
            # Original clip
            self.src_frame = self.clip.get_frame(frame)
            if self.clip.get_error():
                return False
            self.pitch = self.src_frame.get_pitch()
            self.pitchUV = self.src_frame.get_pitch(avisynth.avs.AVS_PLANAR_U)
            self.ptrY = self.src_frame.get_read_ptr()
            if x86_64:
                self.ptrY = self._cffi2ctypes_ptr(self.ptrY)
            if not self.IsY8:
                self.ptrU = self.src_frame.get_read_ptr(avisynth.avs.AVS_PLANAR_U)
                self.ptrV = self.src_frame.get_read_ptr(avisynth.avs.AVS_PLANAR_V)
                if x86_64:
                    self.ptrU = self._cffi2ctypes_ptr(self.ptrU)
                    self.ptrV = self._cffi2ctypes_ptr(self.ptrV)
            # Display clip
            if self.display_clip:
                self.display_frame = self.display_clip.get_frame(frame)
                if self.display_clip.get_error():
                    return False
                self.display_pitch = self.display_frame.get_pitch()
                self.pBits = self.display_frame.get_read_ptr()
                if x86_64:
                    self.pBits = self._cffi2ctypes_ptr(self.pBits)
                if self.RGB48: ## -> RGB24
                    pass
            self.current_frame = frame
            return True
        return False

    def _cffi2ctypes_ptr(self, ptr):
        return ctypes.cast(
                    int(avisynth.ffi.cast('unsigned long long', ptr)),
                    ctypes.POINTER(ctypes.c_ubyte))

    def GetPixelYUV(self, x, y):
        if self.IsPlanar:
            indexY = x + y * self.pitch
            if self.IsY8:
                return (self.ptrY[indexY], -1, -1)
            x = x >> self.WidthSubsampling
            y = y >> self.HeightSubsampling
            indexU = indexV = x + y * self.pitchUV
        elif self.IsYUY2:
            indexY = (x*2) + y * self.pitch
            indexU = 4*(x/2) + 1 + y * self.pitch
            indexV = 4*(x/2) + 3 + y * self.pitch
        else:
            return (-1,-1,-1)
        return (self.ptrY[indexY], self.ptrU[indexU], self.ptrV[indexV])

    def GetPixelRGB(self, x, y, BGR=True):
        if self.IsRGB:
            bytes = self.vi.bytes_from_pixels(1)
            if BGR:
                indexB = (x * bytes) + (self.Height - 1 - y) * self.pitch
                indexG = indexB + 1
                indexR = indexB + 2
            else:
                indexR = (x * bytes) + y * self.pitch
                indexG = indexR + 1
                indexB = indexR + 2
            return (self.ptrY[indexR], self.ptrY[indexG], self.ptrY[indexB])
        else:
            return (-1,-1,-1)

    def GetPixelRGBA(self, x, y, BGR=True):
        if self.IsRGB32:
            bytes = self.vi.bytes_from_pixels(1)
            if BGR:
                indexB = (x * bytes) + (self.Height - 1 - y) * self.pitch
                indexG = indexB + 1
                indexR = indexB + 2
                indexA = indexB + 3
            else:
                indexR = (x * bytes) + y * self.pitch
                indexG = indexR + 1
                indexB = indexR + 2
                indexA = indexB + 3
            return (self.ptrY[indexR], self.ptrY[indexG], self.ptrY[indexB], self.ptrY[indexA])
        else:
            return (-1,-1,-1,-1)

    def GetVarType(self, str_var):
        try:
            return self.env.get_var(str_var, type=True)[1]
        except avisynth.AvisynthError:
            return None

    def IsErrorClip(self):
        return self.error_message is not None

    def BGR2RGB(self, clip):
        '''Reorder AviSynth's RGB (BGR) to RGB

        BGR -> RGB
        BGRA -> RGBA
        '''
        if self.IsRGB:
            clip = self.env.invoke("FlipVertical", clip)
            r = self.env.invoke("ShowRed", clip)
            b = self.env.invoke("ShowBlue", clip)
            if self.IsRGB24:
                return self.env.invoke("MergeRGB", [b, clip, r, 'RGB24'])
            else:
                return self.env.invoke("MergeARGB", [clip, b, clip, r])

    def Y4MHeader(self, colorspace=None, depth=None, width=None, height=None, sar='0:0', X=None):
        '''Return a header for a yuv4mpeg2 stream'''
        re_res = re.compile(r'([x*/])(\d+)')
        if width is None:
            width = self.Width
        elif isinstance(width, basestring):
            match = re_res.match(width)
            if match:
                if match.group(1) == '/':
                    width = self.Width / int(match.group(2))
                else:
                    width = self.Width * int(match.group(2))
            else:
                raise Exception(_('Invalid string: ') + width)
        if height is None:
            height = self.Height
        elif isinstance(height, basestring):
            match = re_res.match(height)
            if match:
                if match.group(1) == '/':
                    height = self.Height / int(match.group(2))
                else:
                    height = self.Height * int(match.group(2))
            else:
                raise Exception(_('Invalid string: ') + height)
        if self.interlaced:
            interlaced = 'b' if self.vi.is_bff() else 't'
        else:
            interlaced = 'p'
        colorspace_dict = {'YV24': '444',
                           'YV16': '422',
                           'YV12': '420',
                           'YV411': '411',
                           'Y8': 'mono'}
        if colorspace is None:
            if self.Colorspace not in colorspace_dict:
                raise Exception(_("{colorspace} can't be used with a yuv4mpeg2 "
                    "header.\nSpecify the right colorspace if piping fake video data.\n"
                    .format(colorspace=self.Colorspace)))
            colorspace = colorspace_dict[self.Colorspace]
        if depth:
            colorspace = 'p'.join((colorspace, str(depth)))
        X = ' X' + X if X is not None else ''
        return 'YUV4MPEG2 W{0} H{1} I{2} F{3}:{4} A{5} C{6}{7}\n'.format(width,
            height, interlaced, self.FramerateNumerator, self.FramerateDenominator,
            sar, colorspace, X)

    def RawFrame(self, frame, y4m_header=False):
        '''Get a buffer of raw video data'''
        if self.initialized:
            if frame < 0:
                frame = 0
            if frame >= self.Framecount:
                frame = self.Framecount - 1
            frame = self.clip.get_frame(frame)
            if self.clip.get_error():
                return
            total_bytes = self.Width * self.Height * self.vi.bits_per_pixel() >> 3
            if y4m_header is not False:
                X = ' X' + y4m_header if isinstance(y4m_header, basestring) else ''
                y4m_header = 'FRAME{0}\n'.format(X)
            else:
                y4m_header = ''
            y4m_header_len = len(y4m_header)
            buf = ctypes.create_string_buffer(total_bytes + y4m_header_len)
            buf[0:y4m_header_len] = y4m_header
            write_addr = ctypes.addressof(buf) + y4m_header_len
            P_UBYTE = ctypes.POINTER(ctypes.c_ubyte)
            if self.IsPlanar and not self.IsY8:
                for plane in (avisynth.avs.AVS_PLANAR_Y, avisynth.avs.AVS_PLANAR_U, avisynth.avs.AVS_PLANAR_V):
                    if x86_64:
                        write_ptr = avisynth.ffi.cast('unsigned char *', write_addr)
                    else:
                        write_ptr = ctypes.cast(write_addr, P_UBYTE)
                    # using get_row_size(plane) and get_height(plane) breaks v2.5.8
                    width = frame.get_row_size() >> self.vi.get_plane_width_subsampling(plane)
                    height = frame.get_height() >> self.vi.get_plane_height_subsampling(plane)
                    self.env.bit_blt(write_ptr, width, frame.get_read_ptr(plane),
                                     frame.get_pitch(plane), width, height)
                    write_addr += width * height
            else:
                # Note that AviSynth uses BGR
                if x86_64:
                    write_ptr = avisynth.ffi.cast('unsigned char *', write_addr)
                else:
                    write_ptr = ctypes.cast(write_addr, P_UBYTE)
                self.env.bit_blt(write_ptr, frame.get_row_size(), frame.get_read_ptr(),
                            frame.get_pitch(), frame.get_row_size(), frame.get_height())
            return buf

    def AutocropFrame(self, frame, tol=70):
        '''Return crop values for a specific frame'''
        width, height = self.Width, self.Height
        if not self._GetFrame(frame):
            return
        GetPixelColor = self.GetPixelRGB if self.IsRGB else self.GetPixelYUV
        w, h = width - 1, height - 1
        top_left0, top_left1, top_left2 = GetPixelColor(0, 0)
        bottom_right0, bottom_right1, bottom_right2 = GetPixelColor(w, h)
        top = bottom = left = right = 0

        # top & bottom
        top_done = bottom_done = False
        for i in range(height):
            for j in range(width):
                if not top_done:
                    color0, color1, color2 = GetPixelColor(j, i)
                    if (abs(color0 - top_left0) > tol or
                        abs(color1 - top_left1) > tol or
                        abs(color2 - top_left2) > tol):
                            top = i
                            top_done = True
                if not bottom_done:
                    color0, color1, color2 = GetPixelColor(j, h - i)
                    if (abs(color0 - bottom_right0) > tol or
                        abs(color1 - bottom_right1) > tol or
                        abs(color2 - bottom_right2) > tol):
                            bottom = i
                            bottom_done = True
                if top_done and bottom_done: break
            else: continue
            break

        # left & right
        left_done = right_done = False
        for j in range(width):
            for i in range(height):
                if not left_done:
                    color0, color1, color2 = GetPixelColor(j, i)
                    if (abs(color0 - top_left0) > tol or
                        abs(color1 - top_left1) > tol or
                        abs(color2 - top_left2) > tol):
                            left = j
                            left_done = True
                if not right_done:
                    color0, color1, color2 = GetPixelColor(w - j, i)
                    if (abs(color0 - bottom_right0) > tol or
                        abs(color1 - bottom_right1) > tol or
                        abs(color2 - bottom_right2) > tol):
                            right = j
                            right_done = True
                if left_done and right_done: break
            else: continue
            break

        return left, top, right, bottom


# on Windows is faster to use DrawDib (VFW)
if os.name == 'nt':

    # Define C types and constants
    DWORD = ctypes.c_ulong
    UINT = ctypes.c_uint
    WORD = ctypes.c_ushort
    LONG = ctypes.c_long
    BYTE = ctypes.c_byte
    CHAR = ctypes.c_char
    HANDLE = ctypes.c_ulong
    NULL = 0
    OF_READ = UINT(0)
    BI_RGB = 0
    GENERIC_WRITE = 0x40000000
    CREATE_ALWAYS = 2
    FILE_ATTRIBUTE_NORMAL  = 0x00000080

    # Define C structures
    class RECT(ctypes.Structure):
        _fields_ = [("left", LONG),
                    ("top", LONG),
                    ("right", LONG),
                    ("bottom", LONG)]

    class BITMAPINFOHEADER(ctypes.Structure):
        _fields_ = [("biSize",  DWORD),
                    ("biWidth",   LONG),
                    ("biHeight",   LONG),
                    ("biPlanes",   WORD),
                    ("biBitCount",   WORD),
                    ("biCompression",  DWORD),
                    ("biSizeImage",  DWORD),
                    ("biXPelsPerMeter",   LONG),
                    ("biYPelsPerMeter",   LONG),
                    ("biClrUsed",  DWORD),
                    ("biClrImportant",  DWORD)]

    class BITMAPFILEHEADER(ctypes.Structure):
        _fields_ = [
            ("bfType",    WORD),
            ("bfSize",   DWORD),
            ("bfReserved1",    WORD),
            ("bfReserved2",    WORD),
            ("bfOffBits",   DWORD)]

    def CreateBitmapInfoHeader(clip, bmih=None):
        vi = clip.get_video_info()
        if bmih is None:
            bmih = BITMAPINFOHEADER()
        bmih.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmih.biWidth = vi.width
        bmih.biHeight = vi.height
        bmih.biPlanes = 1
        if vi.is_rgb32():
            bmih.biBitCount = 32
        elif vi.is_rgb24():
            bmih.biBitCount = 24
        else: raise AvisynthError("Input colorspace is not RGB24 or RGB32")
        bmih.biCompression = BI_RGB
        bmih.biSizeImage = 0 # ignored with biCompression == BI_RGB
        bmih.biXPelsPerMeter = 0
        bmih.biYPelsPerMeter = 0
        bmih.biClrUsed = 0
        bmih.biClrImportant = 0
        return bmih


    # Define C functions

    CreateFile = ctypes.windll.kernel32.CreateFileA
    WriteFile = ctypes.windll.kernel32.WriteFile
    CloseHandle = ctypes.windll.kernel32.CloseHandle

    DrawDibOpen = ctypes.windll.msvfw32.DrawDibOpen
    DrawDibClose = ctypes.windll.msvfw32.DrawDibClose
    DrawDibDraw = ctypes.windll.msvfw32.DrawDibDraw
    handleDib = [None]

    def InitRoutines():
        handleDib[0] = DrawDibOpen()

    def ExitRoutines():
        DrawDibClose(handleDib[0])


    class AvsClip(AvsClipBase):

        def CreateDisplayClip(self, *args, **kwargs):
            if not AvsClipBase.CreateDisplayClip(self, *args, **kwargs):
                return
            # Prepare info header for displaying
            self.bmih = BITMAPINFOHEADER()
            CreateBitmapInfoHeader(self.display_clip, self.bmih)
            self.pInfo = ctypes.pointer(self.bmih)
            return True

        def _ConvertToRGB(self):
            if not self.IsRGB32: # bug in avisynth v2.6 alphas with ConvertToRGB24
                args = [self.display_clip, self.matrix, self.interlaced]
                try:
                    self.display_clip = self.env.invoke("ConvertToRGB32", args)
                except avisynth.AvisynthError as err:
                    return False
            return True

        def _GetFrame(self, frame):
            if AvsClipBase._GetFrame(self, frame):
                self.bmih.biWidth = self.display_pitch * 8 / self.bmih.biBitCount
                return True
            return False

        def DrawFrame(self, frame, dc=None, offset=(0,0), size=None):
            if not self._GetFrame(frame):
                return
            if dc:
                hdc = dc.GetHDC()
                if size is None:
                    w = self.DisplayWidth
                    h = self.DisplayHeight
                else:
                    w, h = size
                row_size = self.display_frame.get_row_size()
                if self.display_pitch == row_size: # the size of the vfb is not guaranteed to be pitch * height unless pitch == row_size
                    pBits = self.pBits
                else:
                    buf = ctypes.create_string_buffer(self.display_pitch * self.DisplayHeight)
                    pBits = ctypes.addressof(buf)
                    ctypes.memmove(pBits, self.pBits, self.display_pitch * (self.DisplayHeight - 1) + row_size)
                DrawDibDraw(handleDib[0], hdc, offset[0], offset[1], w, h,
                            self.pInfo, pBits, 0, 0, w, h, 0)
                return True


# Use generical wxPython drawing support on other platforms
else:

    import wx

    def InitRoutines():
        pass

    def ExitRoutines():
        pass


    class AvsClip(AvsClipBase):

        def _ConvertToRGB(self):
            # There's issues with RGB32, we convert to RGB24
            # AviSynth uses BGR ordering but we need RGB
            try:
                clip = self.display_clip
                if not self.IsRGB24:
                    args = [clip, self.matrix, self.interlaced]
                    clip = self.env.invoke("ConvertToRGB24", args)
                r = self.env.invoke("ShowRed", clip)
                b = self.env.invoke("ShowBlue", clip)
                merge_args = [b, clip, r, "RGB24"]
                self.display_clip = self.env.invoke("MergeRGB", merge_args)
                return True
            except avisynth.AvisynthError as err:
                return False

        def DrawFrame(self, frame, dc=None, offset=(0,0), size=None):
            if not self._GetFrame(frame):
                return
            if dc:
                if size is None:
                    w = self.DisplayWidth
                    h = self.DisplayHeight
                else:
                    w, h = size
                buf = ctypes.create_string_buffer(h * w * 3)
                # Use ctypes.memmove to blit the Avisynth VFB line-by-line
                read_addr = ctypes.addressof(self.pBits.contents) + (h - 1) * self.display_pitch
                write_addr = ctypes.addressof(buf)
                P_UBYTE = ctypes.POINTER(ctypes.c_ubyte)
                for i in range(h):
                    read_ptr = ctypes.cast(read_addr, P_UBYTE)
                    write_ptr = ctypes.cast(write_addr, P_UBYTE)
                    ctypes.memmove(write_ptr, read_ptr, w * 3)
                    read_addr -= self.display_pitch
                    write_addr += w * 3
                bmp = wx.BitmapFromBuffer(w, h, buf)
                dc.DrawBitmap(bmp, 0, 0)
                return True


if __name__ == '__main__':
    AVI = AvsClip('Version().ConvertToYV12()', 'example.avs')
    if AVI.initialized:
        print('Width =', AVI.Width)
        print('Height =', AVI.Height)
        print('Framecount =', AVI.Framecount)
        print('Framerate =', AVI.Framerate)
        print('FramerateNumerator =', AVI.FramerateNumerator)
        print('FramerateDenominator =', AVI.FramerateDenominator)
        print('Audiorate =', AVI.Audiorate)
        print('Audiolength =', AVI.Audiolength)
        #~ print('AudiolengthF =', AVI.AudiolengthF)
        print('Audiochannels =', AVI.Audiochannels)
        print('Audiobits =', AVI.Audiobits)
        print('IsAudioFloat =', AVI.IsAudioFloat)
        print('IsAudioInt =', AVI.IsAudioInt)
        print('Colorspace =', AVI.Colorspace)
        print('IsRGB =', AVI.IsRGB)
        print('IsRGB24 =', AVI.IsRGB24)
        print('IsRGB32 =', AVI.IsRGB32)
        print('IsYUV =', AVI.IsYUV)
        print('IsYUY2 =', AVI.IsYUY2)
        print('IsYV24 =', AVI.IsYV24)
        print('IsYV16 =', AVI.IsYV16)
        print('IsYV12 =', AVI.IsYV12)
        print('IsYV411 =', AVI.IsYV411)
        print('IsY8 =', AVI.IsY8)
        print('IsPlanar =', AVI.IsPlanar)
        print('IsInterleaved =', AVI.IsInterleaved)
        print('IsFieldBased =', AVI.IsFieldBased)
        print('IsFrameBased =', AVI.IsFrameBased)
        print('GetParity =', AVI.GetParity)
        print('HasAudio =', AVI.HasAudio)
        print('HasVideo =', AVI.HasVideo)
    else:
        print(AVI.error_message)
    AVI = None

    AVI = AvsClip('Blackness()', 'test.avs')
    if AVI.initialized:
        print(AVI.Width)
    else:
        print(AVI.error_message)
    AVI = None

    script = """Version().ConvertToYV12()
    Sharpen(1.0)
    FlipVertical()
    """
    env = avisynth.AVS_ScriptEnvironment(3)
    try:
        clip = env.invoke('Eval', script)
    except avisynth.AvisynthError as err:
        print(err)
    else:
        if isinstance(clip, avisynth.AVS_Clip):
            AVI = AvsClip(clip, env=env)
            AVI._GetFrame(100)
            AVI = None
        else:
            print(clip.get_value())
    env = None

    print("Exit program.")

