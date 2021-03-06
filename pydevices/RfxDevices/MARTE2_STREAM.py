#
# Copyright (c) 2017, Massachusetts Institute of Technology All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

from MDSplus import Data

MC = __import__('MARTE2_COMPONENT', globals())


@MC.BUILDER('StreamOut', MC.MARTE2_COMPONENT.MODE_OUTPUT)
class MARTE2_STREAM(MC.MARTE2_COMPONENT):
    inputs = [
        {'name': 'OutStream01', 'type': 'int32', 'dimensions': 0, 'parameters':[
            {'name':'Channel', 'type':'string','value':'CH01'}]},
        {'name': 'OutStream02', 'type': 'float32', 'dimensions': 0, 'parameters':[
            {'name':'Channel', 'type':'string','value':'CH02'}]},
        {'name': 'OutStream03', 'type': 'float32', 'dimensions': 0, 'parameters':[
            {'name':'Channel', 'type':'string','value':'CH03'}]},
        {'name': 'OutStream04', 'type': 'float32', 'dimensions': 0, 'parameters':[
            {'name':'Channel', 'type':'string','value':'CH04'}]},
        {'name': 'OutStream05', 'type': 'float32', 'dimensions': 0, 'parameters':[
            {'name':'Channel', 'type':'string','value':'CH05'}]},
        {'name': 'OutStream06', 'type': 'float32', 'dimensions': 0, 'parameters':[
            {'name':'Channel', 'type':'string','value':'CH06'}]},
        {'name': 'OutStream07', 'type': 'float32', 'dimensions': 0, 'parameters':[
            {'name':'Channel', 'type':'string','value':'CH07'}]},
        {'name': 'OutStream08', 'type': 'float32', 'dimensions': 0, 'parameters':[
            {'name':'Channel', 'type':'string','value':'CH08'}]},
        {'name': 'OutStream09', 'type': 'float32', 'dimensions': 0, 'parameters':[
            {'name':'Channel', 'type':'string','value':'CH09'}]},
        {'name': 'OutStream10', 'type': 'float32', 'dimensions': 0, 'parameters':[
            {'name':'Channel', 'type':'string','value':'CH10'}]},
        {'name': 'OutStream11', 'type': 'float32', 'dimensions': 0, 'parameters':[
            {'name':'Channel', 'type':'string','value':'CH11'}]},
        {'name': 'OutStream12', 'type': 'float32', 'dimensions': 0, 'parameters':[
            {'name':'Channel', 'type':'string','value':'CH12'}]},
        {'name': 'OutStream13', 'type': 'float32', 'dimensions': 0, 'parameters':[
            {'name':'Channel', 'type':'string','value':'CH13'}]},
        {'name': 'OutStream14', 'type': 'float32', 'dimensions': 0, 'parameters':[
            {'name':'Channel', 'type':'string','value':'CH14'}]},
        {'name': 'OutStream15', 'type': 'float32', 'dimensions': 0, 'parameters':[
            {'name':'Channel', 'type':'string','value':'CH15'}]},
        {'name': 'OutStream16', 'type': 'float32', 'dimensions': 0, 'parameters':[
            {'name':'Channel', 'type':'string','value':'CH16'}]},

    ]
    parameters = [
        {'name':'EventDivision', 'type': 'float32'},
        {'name':'ShotNumber', 'type': 'int32'},
        {'name':'TimeIdx', 'type': 'int32', 'value':0},
        {'name':'TimeStreaming', 'type': 'int32', 'value':1},
        {'name':'CpuMask', 'type': 'int32', 'value':15},
        {'name':'StackSize', 'type': 'int32', 'value':10000000},
        {'name':'NumberOfBuffers', 'type': 'int32', 'value':10},
    ]
    parts = []

    def prepareMarteInfo(self):
      if self.parameters_par_4_value.data() == 0: #If oscilloscope mode
        for chanIdx in range(8):
          currInput = getattr(self, 'inputs_outstream%d_value'%(chanIdx+1))
          info = self.getInputChanInfo(currInput)
          if info != None:
            getattr(self, 'inputs_outstream%d_type'%(chanIdx+1)).putData(info['type'])
            if info['samples']!= None and info['samples'] > 1:
              getattr(self, 'inputs_outstream%d_dimensions'%(chanIdx+1)).putData(Data.compile('[$]', info['samples']))
            else:
              if info['dimensions']!= None:
                getattr(self, 'inputs_outstream%d_dimensions'%(chanIdx+1)).putData(info['dimensions'])
