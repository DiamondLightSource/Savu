import os
import numpy as np


rec_header_dtd = \
 [
    ("nx", "i4"),              # Number of columns
    ("ny", "i4"),              # Number of rows
    ("nz", "i4"),              # Number of sections

    ("mode", "i4"),            # Types of pixels in the image. Values used by IMOD:
                               #  0 = unsigned or signed bytes depending on flag in imodFlags
                               #  1 = signed short integers (16 bits)
                               #  2 = float (32 bits)
                               #  3 = short * 2, (used for complex data)
                               #  4 = float * 2, (used for complex data)
                               #  6 = unsigned 16-bit integers (non-standard)
                               # 16 = unsigned char * 3 (for rgb data, non-standard)

    ("nxstart", "i4"),         # Starting point of sub-image (not used in IMOD)
    ("nystart", "i4"),
    ("nzstart", "i4"),

    ("mx", "i4"),              # Grid size in X, Y and Z
    ("my", "i4"),
    ("mz", "i4"),

    ("xlen", "f4"),            # Cell size; pixel spacing = xlen/mx, ylen/my, zlen/mz
    ("ylen", "f4"),
    ("zlen", "f4"),

    ("alpha", "f4"),           # Cell angles - ignored by IMOD
    ("beta", "f4"),
    ("gamma", "f4"),

    # These need to be set to 1, 2, and 3 for pixel spacing to be interpreted correctly
    ("mapc", "i4"),            # map column  1=x,2=y,3=z.
    ("mapr", "i4"),            # map row     1=x,2=y,3=z.
    ("maps", "i4"),            # map section 1=x,2=y,3=z.

    # These need to be set for proper scaling of data
    ("amin", "f4"),            # Minimum pixel value
    ("amax", "f4"),            # Maximum pixel value
    ("amean", "f4"),           # Mean pixel value

    ("ispg", "i4"),            # space group number (ignored by IMOD)
    ("next", "i4"),            # number of bytes in extended header (called nsymbt in MRC standard)
    ("creatid", "i2"),         # used to be an ID number, is 0 as of IMOD 4.2.23
    ("extra_data", "V30"),     # (not used, first two bytes should be 0)

    # These two values specify the structure of data in the extended header; their meaning depend on whether the
    # extended header has the Agard format, a series of 4-byte integers then real numbers, or has data
    # produced by SerialEM, a series of short integers. SerialEM stores a float as two shorts, s1 and s2, by:
    # value = (sign of s1)*(|s1|*256 + (|s2| modulo 256)) * 2**((sign of s2) * (|s2|/256))
    ("nint", "i2"),            # Number of integers per section (Agard format) or number of bytes per section (SerialEM format)
    ("nreal", "i2"),           # Number of reals per section (Agard format) or bit
                               # Number of reals per section (Agard format) or bit
                               # flags for which types of short data (SerialEM format):
                               # 1 = tilt angle * 100  (2 bytes)
                               # 2 = piece coordinates for montage  (6 bytes)
                               # 4 = Stage position * 25    (4 bytes)
                               # 8 = Magnification / 100 (2 bytes)
                               # 16 = Intensity * 25000  (2 bytes)
                               # 32 = Exposure dose in e-/A2, a float in 4 bytes
                               # 128, 512: Reserved for 4-byte items
                               # 64, 256, 1024: Reserved for 2-byte items
                               # If the number of bytes implied by these flags does
                               # not add up to the value in nint, then nint and nreal
                               # are interpreted as ints and reals per section

    ("extra_data2", "V20"),    # extra data (not used)
    ("imodStamp", "i4"),       # 1146047817 indicates that file was created by IMOD
    ("imodFlags", "i4"),       # Bit flags: 1 = bytes are stored as signed

    # Explanation of type of data
    ("idtype", "i2"),          # ( 0 = mono, 1 = tilt, 2 = tilts, 3 = lina, 4 = lins)
    ("lens", "i2"),
    ("nd1", "i2"),             # for idtype = 1, nd1 = axis (1, 2, or 3)
    ("nd2", "i2"),
    ("vd1", "i2"),             # vd1 = 100. * tilt increment
    ("vd2", "i2"),             # vd2 = 100. * starting angle

    # Current angles are used to rotate a model to match a new rotated image.  The three values in each set are
    # rotations about X, Y, and Z axes, applied in the order Z, Y, X.
    ("triangles", "f4", 6),    # 0,1,2 = original:  3,4,5 = current

    ("xorg", "f4"),            # Origin of image
    ("yorg", "f4"),
    ("zorg", "f4"),

    ("cmap", "S4"),            # Contains "MAP "
    ("stamp", "u1", 4),        # First two bytes have 17 and 17 for big-endian or 68 and 65 for little-endian

    ("rms", "f4"),             # RMS deviation of densities from mean density

    ("nlabl", "i4"),           # Number of labels with useful data
    ("labels", "S80", 10)      # 10 labels of 80 charactors
 ]


class MRC(object):

    def __init__(self, X, stats=None):
        self.header = self.header_dict = self.data = None
        self.yz_swapped = False

        if type(X) in [str, unicode]:
            self.read(X)
        else:
            # assuming X to be a numpy array
            self.parse(X, stats=stats)

    def __getitem__(self, item):
        if self.header_dict is not None and \
                item in self.header_dict:
            return self.header_dict[item]
        return None

    def keys(self):
        if self.header_dict is not None:
            return self.header_dict.keys()

    def values(self):
        if self.header_dict is not None:
            return self.header_dict.values()

    def items(self):
        if self.header_dict is not None:
            return self.header_dict.items()

    def parse(self, X, stats=None):
        if stats is not None:
            amin, amax, amean = stats
        else:
            amin = X.min()
            amax = X.max()
            amean = X.mean()

        dt = np.dtype(rec_header_dtd)
        imodFlags = 0
        if X.dtype in [np.uint8, np.int8]:
            mode = 0
            imodFlags = (X.dtype == np.int8)
        elif X.dtype == np.int16:
            mode = 1
        elif X.dtype == np.float32:
            mode = 2
        elif X.dtype == np.complex64:
            mode = 4
        elif X.dtype == np.uint16:
            mode = 6
        else:
            mode = 16

        values = (
            X.shape[2],              # Number of columns
            X.shape[1],              # Number of rows
            X.shape[0],              # Number of sections

            mode,                    # Types of pixels in the image. Values used by IMOD:
                                     #  0 = unsigned or signed bytes depending on flag in imodFlags
                                     #  1 = signed short integers (16 bits)
                                     #  2 = float (32 bits)
                                     #  3 = short * 2, (used for complex data)
                                     #  4 = float * 2, (used for complex data)
                                     #  6 = unsigned 16-bit integers (non-standard)
                                     # 16 = unsigned char * 3 (for rgb data, non-standard)

            0,                       # Starting point of sub-image (not used in IMOD)
            0,
            0,

            X.shape[2],              # Grid size in X, Y and Z
            X.shape[1],
            X.shape[0],

            X.shape[2],            # Cell size; pixel spacing = xlen/mx, ylen/my, zlen/mz
            X.shape[1],
            X.shape[0],

            90.0,           # Cell angles - ignored by IMOD
            90.0,
            90.0,

            # These need to be set to 1, 2, and 3 for pixel spacing to be interpreted correctly
            1,            # map column  1=x,2=y,3=z.
            2,            # map row     1=x,2=y,3=z.
            3,            # map section 1=x,2=y,3=z.

            # These need to be set for proper scaling of data
            amin,            # Minimum pixel value
            amax,            # Maximum pixel value
            amean,           # Mean pixel value

            1,            # space group number (ignored by IMOD)
            0,            # number of bytes in extended header (called nsymbt in MRC standard)
            0,         # used to be an ID number, is 0 as of IMOD 4.2.23
            "",     # (not used, first two bytes should be 0)

            # These two values specify the structure of data in the extended header; their meaning depend on whether the
            # extended header has the Agard format, a series of 4-byte integers then real numbers, or has data
            # produced by SerialEM, a series of short integers. SerialEM stores a float as two shorts, s1 and s2, by:
            # value = (sign of s1)*(|s1|*256 + (|s2| modulo 256)) * 2**((sign of s2) * (|s2|/256))
            0,            # Number of integers per section (Agard format) or number of bytes per section (SerialEM format)
            0,           # Number of reals per section (Agard format) or bit
                                       # Number of reals per section (Agard format) or bit
                                       # flags for which types of short data (SerialEM format):
                                       # 1 = tilt angle * 100  (2 bytes)
                                       # 2 = piece coordinates for montage  (6 bytes)
                                       # 4 = Stage position * 25    (4 bytes)
                                       # 8 = Magnification / 100 (2 bytes)
                                       # 16 = Intensity * 25000  (2 bytes)
                                       # 32 = Exposure dose in e-/A2, a float in 4 bytes
                                       # 128, 512: Reserved for 4-byte items
                                       # 64, 256, 1024: Reserved for 2-byte items
                                       # If the number of bytes implied by these flags does
                                       # not add up to the value in nint, then nint and nreal
                                       # are interpreted as ints and reals per section

            "",    # extra data (not used)
            0,       # 1146047817 indicates that file was created by IMOD
            imodFlags,       # Bit flags: 1 = bytes are stored as signed

            # Explanation of type of data
            0,          # ( 0 = mono, 1 = tilt, 2 = tilts, 3 = lina, 4 = lins)
            0,
            0,             # for idtype = 1, nd1 = axis (1, 2, or 3)
            0,
            0,             # vd1 = 100. * tilt increment
            0,             # vd2 = 100. * starting angle

            # Current angles are used to rotate a model to match a new rotated image.  The three values in each set are
            # rotations about X, Y, and Z axes, applied in the order Z, Y, X.
            [  0.,   0.,   0.,  90.,   0.,   0.],    # 0,1,2 = original:  3,4,5 = current

            0.,            # Origin of image
            X.shape[1] / 2.,
            0.,

            'MAP ',            # Contains "MAP "
            [68, 65,  0,  0],        # First two bytes have 17 and 17 for big-endian or 68 and 65 for little-endian

            0.0,             # RMS deviation of densities from mean density

            6,           # Number of labels with useful data
            [ 'tif2mrc: Converted to mrc format.                       21-Oct-15  13:02:25     ',
              'CCDERASER: Bad points replaced with interpolated values 21-Oct-15  13:03:42     ',
              'NEWSTACK: Images copied, transformed                    21-Oct-15  13:21:42     ',
              'TILT: Tomographic reconstruction                        30-Nov-15  12:29:39     ',
              'NEWSTACK: Images copied             , densities scaled  30-Nov-15  13:59:05     ',
              'clip: flipyz                                            30-Nov-15  13:59:10    ',
              '', '', '', '']      # 10 labels of 80 charactors
        )

        header = np.array(values, dtype=dt)

        header_dict = {}
        for name in header.dtype.names:
            header_dict[name] = header[name]

        self.header = header
        self.data = np.ascontiguousarray(X)
        self.header_dict = header_dict
        return self

#    def read(self, filename):
#        rec_header_dtype = np.dtype(rec_header_dtd)
#        assert rec_header_dtype.itemsize == 1024
#
#        fd = open(filename, 'rb')
#        stats = os.stat(filename)
#
#        header = np.fromfile(fd, dtype=rec_header_dtd, count=1)
#
#        # Seek header
#        #fd.seek(header.itemsize)
#        if header['next'] > 0:
#            fd.seek(header['next']) # ignore extended header
#
#        mode = header['mode']
#        bo = "<" if header['stamp'][0, 0] == 68 and header['stamp'][0, 1] == 65 else "<" # BitOrder: little or big endian
#        sign = "i1" if header['imodFlags'] == 1 else "u1" # signed or unsigned
#                # 0     1     2     3     4     5     6     7     8     9     10    11    12    13    14    15    16
#        dtype = [sign, "i2", "f",  "c4", "c8", None, "u2", None, None, None, None, None, None, None, None, None, "u1"][mode]
#        dsize = [ 1,    2,    4,    4,    8,    0,    2,    0,    0,    0,    0,    0,    0,    0,    0,    0,    3][mode]
#
#        # data dimensions
#        nx, ny, nz = header['nx'], header['ny'], header['nz']
#        img_size = nx * ny * nz * dsize
#        img_str = fd.read(img_size)
#        dtype = bo + dtype
#
#        # Make sure that we have readed the whole file
#        assert not fd.read(), "Error loading the file"
#        #assert stats.st_size == header.itemsize + img_size
#
#        fd.close()
#
#        if mode == 16:
#            data = np.ndarray(shape=(nx, ny, nz, 3), dtype=dtype, buffer=img_str, order='F')
#        else:
#            data = np.ndarray(shape=(nx, ny, nz), dtype=dtype, buffer=img_str, order='F')
#
#        data = np.swapaxes(data, 0, 2)
#
#        header_dict = {}
#        for name in header.dtype.names:
#            header_dict[name] = header[name][0] if len(header[name]) == 1 else header[name]
#
#        self.header = header
#        self.data = np.ascontiguousarray(data)
#        self.header_dict = header_dict
#        return self
        
    def read(self, filename, index):
        pass
        

    def save(self, filename):
        fd = open(filename, 'wb')
        fd.write(self.header.data)
        data = self.data
        data = np.swapaxes(data, 0, 2)
        if self.yz_swapped:
            data = np.swapaxes(data, 1, 2)
        data = np.asfortranarray(data)
        fd.write(data.data)
        fd.close()