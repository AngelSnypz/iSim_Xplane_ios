import socket
import struct

class XPlaneConnect(object):
    '''XPlaneConnect (XPC) facilitates communication to and from the XPCPlugin.'''
    socket = None
    systemIP = '0'

    # Basic Functions
    def __init__(self, xpHost, xpPort = 49009, port = 49010, timeout = 50000):
        global systemIP
        #def __init__(self, xpHost='localhost', xpPort=49009, port=49010, timeout=30000):
        '''Sets up a new connection to an X-Plane Connect plugin running in X-Plane.
        
            Args:
              xpHost: The hostname of the machine running X-Plane.
              xpPort: The port on which the XPC plugin is listening. Usually 49007.
              port: The port which will be used to send and receive data.
              timeout: The period (in milliseconds) after which read attempts will fail.
        '''

        # Validate parameters
        xpIP = None
        try:
            xpIP = socket.gethostbyname(xpHost)
            systemIP=xpIP
        except:
            raise ValueError("Unable to resolve xpHost.")

        if xpPort < 0 or xpPort > 65535:
            raise ValueError("The specified X-Plane port is not a valid port number.")
        if port < 0 or port > 65535:
            raise ValueError("The specified port is not a valid port number.")
        if timeout < 0:
            raise ValueError("timeout must be non-negative.")

        # Setup XPlane IP and port
        self.xpDst = (xpIP, xpPort)

        # Create and bind socket        
        clientAddr = ("0.0.0.0", port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.bind(clientAddr)
        timeout /= 1000.0
        self.socket.settimeout(timeout)

    def __del__(self):
        self.close()

    # Define __enter__ and __exit__ to support the `with` construct.
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        '''Closes the specified connection and releases resources associated with it.'''
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def sendCommand(self, command):
        global  systemIP
        udpport=49000
        buffer=struct.pack('<4sx',"CMND")
        fmt = str(len(command))+'s'
        data=command
        buffer+=struct.pack(fmt,data)
        while(len(buffer)<64+5):
            buffer+=struct.pack('x')
        self.socket.sendto(buffer,(systemIP,udpport))

    def pauseXplane(self):
        global systemIP
        #udpip='localhost'
        udpport=49000
        buffer=struct.pack('<4sx',"CMND")
        fmt='26s'
        data="sim/operation/pause_toggle"
        buffer+=struct.pack(fmt,data)
        while(len(buffer)<64+5):
            buffer+=struct.pack('x')
        self.socket.sendto(buffer,(systemIP,udpport))
        
    def repairAll(self):
        global systemIP
        buffer=struct.pack('<4sx','RESE')
        while(len(buffer)<64+5):
            buffer+=struct.pack('x')
        #udp_ip = 'localhost'
        udp_port=49000
        sock =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.sendto(buffer,(systemIP,udp_port))


    def sendNfal(self,navaid):
        global systemIP
        udpport = 49000
        buffer = struct.pack('<4sx', "NFAL")
        navaids=list(navaid)
        for x in navaids:
            buffer+=struct.pack('c',x)
        #while (len(buffer) < 64 + 5):
        #   buffer += struct.pack('x')
        self.socket.sendto(buffer, (systemIP, udpport))
        print 'failed stuff'

    def sendPREL(self,startpos,airportcode):
        #udpip='localhost'
        global systemIP
        udpport=49000
        buffer=struct.pack('<4sx',"PREL")
        start=startpos                #different starts as per the rtf files
        index=0                 #index of aircraft. stays at 0
        airportcodesplit=list(airportcode)
        code1=airportcodesplit[0]
        code2=airportcodesplit[1]
        code3=airportcodesplit[2]
        code4=airportcodesplit[3]
        #Add in Runway number Selection: xint apt_rwy_idx;	// runway index
        #Add in Runway Direction:        xint apt_rwy_dir;  // runway dir

        '''print code1
        print code2
        print code3
        print code4'''

        fmt="2i4c"
        buffer+=struct.pack(fmt,start,index,code1,code2,code3,code4)
        while(len(buffer)<64+5):
            buffer+=struct.pack('x')
        self.socket.sendto(buffer,(systemIP,udpport))

    def sendACPR(self, startpos, airportcode):
        # udpip='localhost'
        global systemIP
        udpport = 49000
        #buffer = struct.pack('<4sx', "ACPR")
        aircraft=0
        pathtoaircraft="Aircraft/AS350B3 Plus/AS350B3.acf"
        sLen=len(pathtoaircraft)
        liveryindex=0
        fmt="<4sxi"+str(sLen)+"sxix"
        acfnbuffer=struct.pack(fmt,"ACFN",aircraft,pathtoaircraft,liveryindex)


        start = startpos  # different starts as per the rtf files
        index = 0  # index of aircraft. stays at 0
        airportcodesplit = list(airportcode)
        code1 = airportcodesplit[0]
        code2 = airportcodesplit[1]
        code3 = airportcodesplit[2]
        code4 = airportcodesplit[3]
        # Add in Runway number Selection: xint apt_rwy_idx;	// runway index
        # Add in Runway Direction:        xint apt_rwy_dir;  // runway dir

        '''print code1
        print code2
        print code3
        print code4'''

        fmt = "<4sx2i4c"
        prelbuf=struct.pack(fmt,"PREL", start, index, code1, code2, code3, code4)

        #buffer+=acfnbuffer
        #buffer+=prelbuf

        #buffer += struct.pack(fmt, start, index, code1, code2, code3, code4)
        while (len(acfnbuffer) < 160 +5) :
            acfnbuffer += struct.pack('x')
        while (len(prelbuf)<64+5):
            prelbuf+=struct.pack('x')


        self.socket.sendto(prelbuf,(systemIP,udpport))
        self.socket.sendto(acfnbuffer, (systemIP, udpport))
       
    def sendUDP(self, buffer):
        '''Sends a message over the underlying UDP socket.'''
        # Preconditions
        if(len(buffer) == 0):
            raise ValueError("sendUDP: buffer is empty.")

        self.socket.sendto(buffer, 0, self.xpDst)

    def readUDP(self):
        '''Reads a message from the underlying UDP socket.'''
        return self.socket.recv(16384)

    # Configuration
    def setCONN(self, port):
        '''Sets the port on which the client sends and receives data.
        
            Args:
              port: The new port to use.
        '''
        #Validate parameters        
        if port < 0 or port > 65535:
            raise ValueError("The specified port is not a valid port number.")

        #Send command
        buffer = struct.pack("<4sxH", "CONN", port)
        self.sendUDP(buffer)
        
        #Rebind socket
        clientAddr = ("0.0.0.0", port)
        timeout = self.socket.gettimeout();
        self.socket.close();
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.bind(clientAddr)
        self.socket.settimeout(timeout)

        #Read response
        buffer = self.socket.recv(1024)

    def pauseSim(self, pause):
        '''Pauses or un-pauses the physics simulation engine in X-Plane.
        
            Args:
              pause: True to pause the simulation; False to resume.
        '''
        pause = int(pause)
        if pause < 0 or pause > 2:
            raise ValueError("Invalid argument for pause command.")

        buffer = struct.pack("<4sxB", "SIMU", pause) #4 chars, ???, number to binary (1 or 0)
        self.sendUDP(buffer)

    # X-Plane UDP Data
    def readDATA(self):
        '''Reads X-Plane data.
        
            Returns: A 2 dimensional array containing 0 or more rows of data. Each array
              in the result will have 9 elements, the first of which is the row number which
              that array represents data for, and the rest of which are the data elements in
              that row.
        '''
        buffer = self.readUDP();
        if len(buffer) < 6:
            return None
        rows = (len(buffer) - 5) / 36
        data = []
        for i in range(rows):
            data.append(struct.unpack_from("9f", buffer, 5 + 36*i))
        return data

    def sendDATA(self, data):
        '''Sends X-Plane data over the underlying UDP socket.
        
            Args:
              data: An array of values representing data rows to be set. Each array in `data`
                should have 9 elements, the first of which is a row number in the range (0-134),
                and the rest of which are the values to set for that data row.
        '''
        if len(data) > 134:
            raise ValueError("Too many rows in data.")

        buffer = struct.pack("<4sx", "DATA")
        for row in data:
            if len(row) != 9:
                raise ValueError("Row does not contain exactly 9 values. <" + str(row) + ">")
            buffer += struct.pack("<I8f", *row)
        self.sendUDP(buffer)

    # Position    
    def getPOSI(self, ac = 0):
        '''Gets position information for the specified aircraft.

        Args:
          ac: The aircraft to set the control surfaces of. 0 is the main/player aircraft.
        '''
        # Send request
        buffer = struct.pack("<4sxB", "GETP", ac)
        self.sendUDP(buffer)

        # Read response
        resultBuf = self.readUDP()
        if len(resultBuf) != 34:
            raise ValueError("Unexpected response length.")

        result = struct.unpack("<4sxBfffffff", resultBuf)
        if result[0] != "POSI":
            raise ValueError("Unexpected header: " + result[0])

        # Drop the header & ac from the return value
        return result[2:]

    def sendPOSI(self, values, ac = 0):
        '''Sets position information on the specified aircraft.

            Args:
              values: The position values to set. `values` is a array containing up to
                7 elements. If less than 7 elements are specified or any elment is set to `-998`,
                those values will not be changed. The elements in `values` corespond to the
                following:
                  * Latitude (deg)
                  * Longitude (deg)
                  * Altitude (m above MSL)
                  * Pitch (deg)
                  * Roll (deg)
                  * True Heading (deg)
                  * Gear (0=up, 1=down)
              ac: The aircraft to set the control surfaces of. 0 is the main/player aircraft.
        '''
        # Preconditions
        if len(values) < 1 or len(values) > 7:
            raise ValueError("Must have between 0 and 7 items in values.")
        if ac < 0 or ac > 20:
            raise ValueError("Aircraft number must be between 0 and 20.")

        # Pack message
        buffer = struct.pack("<4sxB", "POSI", ac)
        for i in range(7):
            val = -998
            if i < len(values):
                val = values[i]
            buffer += struct.pack("<f", val)

        # Send
        self.sendUDP(buffer)

    # Controls
    def getCTRL(self, ac = 0):
        '''Gets the control surface information for the specified aircraft.

        Args:
          ac: The aircraft to set the control surfaces of. 0 is the main/player aircraft.
        '''
        # Send request
        buffer = struct.pack("<4sxB", "GETC", ac)
        self.sendUDP(buffer)

        # Read response
        resultBuf = self.readUDP()
        if len(resultBuf) != 31:
            raise ValueError("Unexpected response length.")

        result = struct.unpack("<4sxffffbfBf", resultBuf)
        if result[0] != "CTRL":
            raise ValueError("Unexpected header: " + result[0])

        # Drop the header from the return value
        result =result[1:7] + result[8:]
        return result

    def sendCTRL(self, values, ac = 0):
        '''Sets control surface information on the specified aircraft.

            Args:
              values: The control surface values to set. `values` is a array containing up to
                6 elements. If less than 6 elements are specified or any elment is set to `-998`,
                those values will not be changed. The elements in `values` corespond to the
                following:
                  * Latitudinal Stick [-1,1]
                  * Longitudinal Stick [-1,1]
                  * Rudder Pedals [-1, 1]
                  * Throttle [-1, 1]
                  * Gear (0=up, 1=down)
                  * Flaps [0, 1]
                  * Speedbrakes [-0.5, 1.5]
              ac: The aircraft to set the control surfaces of. 0 is the main/player aircraft.
        '''
        # Preconditions
        if len(values) < 1 or len(values) > 7:
            raise ValueError("Must have between 0 and 6 items in values.")
        if ac < 0 or ac > 20:
            raise ValueError("Aircraft number must be between 0 and 20.")

        # Pack message
        buffer = struct.pack("<4sx", "CTRL")
        for i in range(6):
            val = -998
            if i < len(values):
                val = values[i]
            if i == 4:
                val = -1 if (abs(val + 998) < 1e-4) else val
                buffer += struct.pack("b", val)
            else:
                buffer += struct.pack("<f", val)
        buffer += struct.pack("B", ac)
        if len(values) == 7:
            buffer += struct.pack("<f", values[6])

        # Send
        self.sendUDP(buffer)
        
    # DREF Manipulation    
    def sendDREF(self, dref, values):
        '''Sets the specified dataref to the specified value.

            Args:
              dref: The name of the datarefs to set.
              values: Either a scalar value or a sequence of values.
        '''
        self.sendDREFs([dref], [values])

    def sendDREFs(self, drefs, values):
        '''Sets the specified datarefs to the specified values.

            Args:
              drefs: A list of names of the datarefs to set.
              values: A list of scalar or vector values to set.
        '''
        if len(drefs) != len(values):
            raise ValueError("drefs and values must have the same number of elements.")

        buffer = struct.pack("<4sx", "DREF")
        for i in range(len(drefs)):
            dref = drefs[i]
            value = values[i]
            # Preconditions
            if len(dref) == 0 or len(dref) > 255:
                raise ValueError("dref must be a non-empty string less than 256 characters.")
            if value == None:
                raise ValueError("value must be a scalar or sequence of floats.")
        
            # Pack message
            if hasattr(value, "__len__"):
                if len(value) > 255:
                    raise ValueError("value must have less than 256 items.")
                fmt = "<B{0:d}sB{1:d}f".format(len(dref), len(value))
                buffer += struct.pack(fmt, len(dref), dref, len(value), value)
            else:
                fmt = "<B{0:d}sBf".format(len(dref))
                buffer += struct.pack(fmt, len(dref), dref, 1, value)

        # Send
        self.sendUDP(buffer)

    def getDREF(self, dref):
        '''Gets the value of an X-Plane dataref.
            
            Args:
              dref: The name of the dataref to get.

            Returns: A sequence of data representing the values of the requested dataref.
        '''
        return self.getDREFs([dref])[0]

    def getDREFs(self, drefs):
        '''Gets the value of one or more X-Plane datarefs.

            Args:
              drefs: The names of the datarefs to get.

            Returns: A multidimensional sequence of data representing the values of the requested
             datarefs.
        '''
        # Send request
        buffer = struct.pack("<4sxB", "GETD", len(drefs))
        for dref in drefs:
            fmt = "<B{0:d}s".format(len(dref))
            buffer += struct.pack(fmt, len(dref), dref)
        self.sendUDP(buffer)

        # Read and parse response
        buffer = self.readUDP()
        resultCount = struct.unpack_from("B", buffer, 5)[0]
        offset = 6
        result = []
        for i in range(resultCount):
            rowLen = struct.unpack_from("B", buffer, offset)[0]
            offset += 1
            fmt = "<{0:d}f".format(rowLen)
            row = struct.unpack_from(fmt, buffer, offset)
            result.append(row)
            offset += rowLen * 4
        return result

    # Drawing
    def sendTEXT(self, msg, x = -1, y = -1):
        '''Sets a message that X-Plane will display on the screen.

            Args:
              msg: The string to display on the screen
              x: The distance in pixels from the left edge of the screen to display the
                 message. A value of -1 indicates that the default horizontal position should
                 be used.
              y: The distance in pixels from the bottom edge of the screen to display the
                 message. A value of -1 indicates that the default vertical position should be
                 used.
        '''
        if y < -1:
            raise ValueError("y must be greater than or equal to -1.")

        if msg == None:
            msg = ""

        msgLen = len(msg)
        buffer = struct.pack("<4sxiiB" + str(msgLen) + "s", "TEXT", x, y, msgLen, msg)
        self.sendUDP(buffer)

    def sendVIEW(self, view):
        '''Sets the camera view in X-Plane

            Args:
              view: The view to use. The ViewType class provides named constants
                    for known views.
        '''
        # Preconditions
        if view < ViewType.Forwards or view > ViewType.FullscreenNoHud:
            raise ValueError("Unknown view command.")

        # Pack buffer
        buffer = struct.pack("<4sxi", "VIEW", view)

        # Send message
        self.sendUDP(buffer)

    def sendWYPT(self, op, points):
        '''Adds, removes, or clears waypoints. Waypoints are three dimensional points on or
           above the Earth's surface that are represented visually in the simulator. Each
           point consists of a latitude and longitude expressed in fractional degrees and
           an altitude expressed as meters above sea level.

            Args:
              op: The operation to perform. Pass `1` to add waypoints,
                `2` to remove waypoints, and `3` to clear all waypoints.
              points: A sequence of floating point values representing latitude, longitude, and
                altitude triples. The length of this array should always be divisible by 3.
        '''
        if op < 1 or op > 3:
            raise ValueError("Invalid operation specified.")
        if len(points) % 3 != 0:
            raise ValueError("Invalid points. Points should be divisible by 3.")
        if len(points) / 3 > 255:
            raise ValueError("Too many points. You can only send 255 points at a time.")

        if op == 3:
            buffer = struct.pack("<4sxBB", "WYPT", 3, 0)
        else:
            buffer = struct.pack("<4sxBB" + str(len(points)) + "f", "WYPT", op, len(points), *points)
        self.sendUDP(buffer)

class ViewType(object):
    Forwards = 73
    Down = 74
    Left = 75
    Right = 76
    Back = 77
    Tower = 78
    Runway = 79
    Chase = 80
    Follow = 81
    FollowWithPanel = 82
    Spot = 83
    FullscreenWithHud = 84
    FullscreenNoHud = 85
