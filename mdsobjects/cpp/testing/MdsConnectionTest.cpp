/*
Copyright (c) 2017, Massachusetts Institute of Technology All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#include "testutils/MdsIpInstancer.h"
#include <unistd.h>
#include <fstream>
#include <sys/types.h>
#include <signal.h>

#include <mdsobjects.h>

#include "testutils/testutils.h"
#include "testutils/unique_ptr.h"
#include "testing.h"

#ifdef _WIN32
#define setenv(name,val,extra) _putenv_s(name,val)
#endif

//
// TODO: Finish tests with PutMany and GetMany ...
//

using namespace MDSplus;
using namespace testing;




void _test_tree_open(const char *prot, const unsigned short port, const char* mode){
    MdsIpInstancer mdsip(prot,port,mode);
    std::string addr = mdsip.getAddress();
    std::cout << "attempt to connect to: " << addr;
    if (mode) std::cout << " (" << mode <<")";
    std::cout << "\n" << std::flush;
    unique_ptr<Connection> cnx = NULL;
    int retry = 3;
    for (;!cnx; retry--) try {
      cnx = new Connection(const_cast<char*>(addr.c_str()));
    } catch (...) {
      if (retry<=1) TEST0("could not connect");
      std::cout << "retry\n" << std::flush;
      usleep(500000);
    }
    std::cout << "success: starting test\n" << std::flush;
    // test client-server communication //
    unique_ptr<Data> data = cnx->get("ZERO(10)");

    data = cnx->get("DECOMPILE(`TreeShr->TreeDbid:P())");
    TEST0( AutoString(data->getString()).string == "Pointer(0)" );

    data = cnx->get("setTimeContext()");
    TEST1(data->getInt() == 1 && "setTimeContext()");

    // test tree opening //
    data = cnx->get("setenv('t_connect_path=.')");
    cnx->openTree((char*)"t_connect",1);

    Data *args[] = { new Int32(5552368),
                     new Float64(111.234) };
    cnx->put("test_cnx",(char*)"$+10",args,1);
    data = cnx->get("test_cnx");
    TEST1( data->getInt() == 5552378 && "$+10");

    cnx->put("test_cnx",(char*)"[$1+10, $2]",args,2);
    data = cnx->get("test_cnx");
    TEST1( AutoString(data->getString()).string == "[5552378D0,111.234D0]" );

    cnx->put("test_cnx",(char*)"5552368",NULL,0);
    data = cnx->get("test_cnx");
    TEST1( data->getInt() == 5552368 && "5552368" );

    deleteData(args[0]);
    deleteData(args[1]);

    // closing tree //
    cnx->closeTree((char*)"t_connect",1);
}

void test_tree_open(const char *prot, const unsigned short port, const char* mode){
  try {
    _test_tree_open(prot, port, mode);
  } catch (...) {
    TEST0("exception");
  }
}

////////////////////////////////////////////////////////////////////////////////
//  main  //////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////



int main(int argc UNUSED_ARGUMENT, char *argv[] UNUSED_ARGUMENT)
{
    TEST_TIMEOUT(30);
    setenv("t_connect_path",".",1);

#ifdef _WIN32
    WSADATA wsaData;
    WORD wVersionRequested;
    wVersionRequested = MAKEWORD(1, 1);
    WSAStartup(wVersionRequested, &wsaData);
#endif

    ////////////////////////////////////////////////////////////////////////////////
    //  Generate Tree  /////////////////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////

    // this makes the t_connect in a separate process so that all static
    // variables instanced are destroied when the child ends.
    try {
      unique_ptr<Tree> tree = new Tree("t_connect",-1,"NEW");
      unique_ptr<TreeNode>(tree->addNode("test_cnx","NUMERIC"));
      tree->write();
      tree->edit(false);
      tree->createPulse(1);
    } catch (...) {
      std::cerr << "Error creating model tree";
    }

    ////////////////////////////////////////////////////////////////////////////////
    //  TEST CONNECTION TO REMOTE TREE  ////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////

    // local  (includes: ssh, htmp) //
    BEGIN_TESTING(Connection local);
    test_tree_open("local",0,NULL);
    END_TESTING;

    // tcp //
    BEGIN_TESTING(Connection tcp);
    test_tree_open("tcp",8600,"-s");
    test_tree_open("tcp",8601,"-m");
    END_TESTING;
/*
    // tcpv6 //
    BEGIN_TESTING(Connection tcpv6);
    test_tree_open("tcpv6",8604,"-s");
    test_tree_open("tcpv6",8605,"-m");
    END_TESTING;
*/
#ifndef _WIN32
    // udt //
    BEGIN_TESTING(Connection udt);
    test_tree_open("udt",8602,"-s");
    test_tree_open("udt",8603,"-m");
    END_TESTING;
/*
    // udtv6 //
    BEGIN_TESTING(Connection udtv6);
    test_tree_open("udtv6",8606,"-s");
    test_tree_open("udtv6",8607,"-m");
    END_TESTING;
*/
#endif
/*
// TODO: gsi test does not work (gsi setup?)
// ERROR:Error connecting ---
//       globus_xio_gsi: gss_init_sec_context failed.
//
// ERROR:mdsip_accept_cp, open ---
//       globus_xio: The GSI XIO driver failed to establish a secure connection. The failure occured during a handshake read.

    // gsi //
    BEGIN_TESTING(Connection gsi);
    test_tree_open("gsi",8608,"-s");
    test_tree_open("gsi",8608,"-m");
    END_TESTING;
*/
}
