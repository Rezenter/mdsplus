#!/usr/bin/python
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

import sys
from time import sleep
from re import match
from MDSplus import Tree,Device,Connection,GetMany,Range
from MDSplus import dcl,ccl,tcl,cts,mdsExceptions as Exc

def _mimport(name, level=1):
    try:
        return __import__(name, globals(), level=level)
    except:
        return __import__(name, globals())
_UnitTest=_mimport("_UnitTest")
class Tests(_UnitTest.TreeTests,_UnitTest.MdsIp):
    shotinc = 1
    tree = 'pytree'
    def _doTCLTest(self,expr,out=None,err=None,re=False,tcl=tcl):
        def checkre(pattern,string):
            if pattern is None:
                self.assertEqual(string is None,True)
            else:
                self.assertEqual(string is None,False)
                self.assertEqual(match(pattern,str(string)) is None,False,'"%s"\nnot matched by\n"%s"'%(string,pattern))
        if Tests.debug: sys.stderr.write("TCL(%s)\n"%(expr,));
        outerr = tcl(expr,True,True,True)
        if not re:
            self.assertEqual(outerr,(out,err))
        else:
            checkre(out,outerr[0])
            checkre(err,outerr[1])

    def _doExceptionTest(self,expr,exc):
        if Tests.debug: sys.stderr.write("TCL(%s) # expected exception: %s\n"%(expr,exc.__name__));
        try:
            tcl(expr,True,True,True)
        except Exception as e:
            self.assertEqual(e.__class__,exc)
            return
        self.fail("TCL: '%s' should have signaled an exception"%expr)

    def interface(self):
        with Tree(self.tree,self.shot,'new') as pytree:
            Device.PyDevice('TestDevice').Add(pytree,'TESTDEVICE')
            pytree.write()
        self.assertEqual(dcl('help set verify',1,1,0)[1],None)
        self.assertEqual(tcl('help set tree',1,1,0)[1],None)
        self.assertEqual(ccl('help set xandq',1,1,0)[1],None)
        self.assertEqual(cts('help addcrate',1,1,0)[1],None)
        """ tcl commands """
        self._doTCLTest('type test','test\n')
        if self.inThread: Tree.usePrivateCtx(1)
        self._doTCLTest('close/all')
        self._doTCLTest('show db','\n')
        self._doTCLTest('set tree pytree/shot=%d'%(self.shot,))
        self._doTCLTest('show db','000  PYTREE        shot: %d [\\PYTREE::TOP]   \n\n'%self.shot)
        self._doTCLTest('edit PYTREE/shot=%d'%(self.shot,))
        self._doTCLTest('add node TCL_NUM/usage=numeric')
        self._doTCLTest('add node TCL_PY_DEV/model=TESTDEVICE')
        self._doTCLTest('do TESTDEVICE:TASK_TEST')
        self._doExceptionTest('do TESTDEVICE:TASK_ERROR1',Exc.DevUNKOWN_STATE)
        self._doExceptionTest('do TESTDEVICE:TASK_ERROR2',Exc.DevUNKOWN_STATE)
        self._doExceptionTest('close',Exc.TreeWRITEFIRST)
        self._doTCLTest('write')
        self._doTCLTest('close')
        self._doTCLTest('show db','\n')
        """ context """
        self._doTCLTest('set tree pytree/shot=%d'%(self.shot,))
        pytree = Tree()
        self.assertEqual(str(pytree),'Tree("PYTREE",%d,"Normal")'%self.shot)
        self._doTCLTest('close pytree/shot=%d'%(self.shot,))
        self.assertEqual(str(pytree),'Tree("?",?,"Closed")')
        if self.inThread: Tree.usePrivateCtx(0)
        """ tcl exceptions """
        self._doExceptionTest('close',Exc.TreeNOT_OPEN)
        self._doExceptionTest('dispatch/command/server=xXxXxXx type test',Exc.ServerPATH_DOWN)
        self._doExceptionTest('dispatch/command/server type test',Exc.MdsdclIVVERB)

    def dispatcher(self):
        shot = self.shot+1
        with Tree(self.tree,shot,'new') as pytree:
            Device.PyDevice('TestDevice').Add(pytree,'TESTDEVICE')
            pytree.write()
        monitor,monitor_port = self._setup_mdsip('ACTION_MONITOR','MONITOR_PORT',7010+self.index,False)
        monitor_opt = "/monitor=%s"%monitor if monitor_port>0 else ""
        server ,server_port  = self._setup_mdsip('ACTION_SERVER', 'ACTION_PORT',7000+self.index,True)
        show_server = "Checking server: %s\n[^,]+, [^,]+, logging enabled, Inactive\n"%server
        pytree.normal()
        pytree.TESTDEVICE.ACTIONSERVER.no_write_shot = False
        pytree.TESTDEVICE.ACTIONSERVER.record = server
        """ using dispatcher """
        mon,mon_log,svr,svr_log = (None,None,None,None)
        try:
            mon,mon_log = self._start_mdsip(monitor,monitor_port,'monitor')
            svr,svr_log = self._start_mdsip(server ,server_port ,'server',self.env)
            try:
                if mon or svr: sleep(1)
                if mon: self.assertEqual(mon.poll(),None)
                if svr: self.assertEqual(svr.poll(),None)
                """ mdsconnect """
                c = Connection(server)
                self.assertEqual(c.get('1').tolist(),1)
                self.assertEqual(c.getObject('1:3:1').__class__,Range)
                g = GetMany(c);
                g.append('a','1')
                g.append('b','$',2)
                g.append('c','$+$',1,2)
                g.execute()
                self.assertEqual(g.get('a'),1)
                self.assertEqual(g.get('b'),2)
                self.assertEqual(g.get('c'),3)
                """ tcl dispatch """
                self._doTCLTest('show server %s'%server,out=show_server,re=True)
                self._testDispatchCommand(server,'set verify')
                self._testDispatchCommand(server,'type test')
                self._doTCLTest('set tree pytree/shot=%d'%shot)
                self._doTCLTest('dispatch/build%s'%monitor_opt)
                self._doTCLTest('dispatch/phase%s INIT'%monitor_opt)
                sleep(.1)
                self._doTCLTest('show server %s'%server,out=show_server,re=True)
                self._doTCLTest('dispatch/phase%s PULSE'%monitor_opt)
                sleep(.1)
                self._doTCLTest('show server %s'%server,out=show_server,re=True)
                self._doTCLTest('dispatch/phase%s STORE'%monitor_opt)
                sleep(.1)
                self._doTCLTest('show server %s'%server,out=show_server,re=True)
                """ tcl exceptions """
                self._doExceptionTest('dispatch/command/server=%s '%server,Exc.MdsdclIVVERB)
                """ tcl check if still alive """
                if mon: self.assertEqual(mon.poll(),None)
                if svr: self.assertEqual(svr.poll(),None)
            finally:
                if svr and svr.poll() is None:
                    svr.terminate()
                    svr.wait()
                else:
                    try: self._doTCLTest('dispatch/command/wait/server=%s close/all'%server)
                    except: pass
                if mon and mon.poll() is None:
                    mon.terminate()
                    mon.wait()
        finally:
            if svr_log: svr_log.close()
            if mon_log: mon_log.close()
            self._doTCLTest('close/all')
        pytree.readonly()
        self.assertTrue(pytree.TESTDEVICE.INIT1_DONE.record <= pytree.TESTDEVICE.INIT2_DONE.record)

    def timeout(self,full=False):
        def test_timeout(c,expr,to):
            with c:
                try: # break out of sleep
                    c.get('write(2,"tic: "//"%s");%s;write(2,"toc: "//"%s")'%(expr,expr,expr),timeout=to)
                    self.fail('Connection.get("%s") should have timed out.'%expr)
                except Exc.MDSplusException as e:
                    self.assertEqual(e.__class__,Exc.TdiTIMEOUT)
        server,server_port  = self._setup_mdsip('ACTION_SERVER', 'ACTION_PORT',7000+self.index,True)
        svr = svr_log = None
        try:
            svr,svr_log = self._start_mdsip(server ,server_port ,'timeout',self.env)
            try:
                if svr:
                    sleep(1)
                    self.assertEqual(svr.poll(),None)
                c = Connection(server)
                c.get("py('1')") # preload MDSplus on server
                test_timeout(c,"wait(3)",1000) # break tdi wait
                test_timeout(c,"py('from time import sleep;sleep(3)')",1500) # break python sleep
                if full: # timing too unreliable for standard test
                    test_timeout(c,"for(;1;) ;",100) # break tdi inf.loop
                    test_timeout(c,"py('while 1: pass')",500) # break python inf.loop
                c.get("1")
            finally:
                if svr and svr.poll() is None:
                    svr.terminate()
                    svr.wait()
        finally:
            if svr_log: svr_log.close()
    def timeoutfull(self): self.timeout(full=True)

    @staticmethod
    def getTests():
        lst = ['interface']
        if Tests.inThread: return lst
        lst.append('dispatcher')
        if sys.platform.startswith('win') or sys.maxsize > 1<<32:
            lst.append('timeout')
        return lst

Tests.main(__name__)
