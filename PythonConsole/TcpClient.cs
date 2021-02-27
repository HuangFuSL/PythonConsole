﻿using ColossalFramework.IO;
using SkylinesPythonShared;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Runtime.Serialization.Formatters.Binary;
using System.Text;

namespace PythonConsole
{
    public class TcpClient : TcpConversation
    {
        public static Process process;
        public static TcpClient CreateClient()
        {
            Socket s = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            s.Connect(IPAddress.Parse("127.0.0.1"), 6672);
            return new TcpClient(s);
        }
        protected TcpClient(Socket s) : base(s)
        {
            
        }

        public static void StartUpServer()
        {
            string archivePath = Path.Combine(ModPath.Instsance.AssemblyPath,"SkylinesRemotePython.zip");
            string destPath = Path.Combine(DataLocation.executableDirectory, "SkylinesRemotePython");

            using (var unzip = new Unzip(archivePath))
            {
                unzip.ExtractToDirectory(destPath);
            }
            process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = Path.Combine(destPath, "SkylinesRemotePythonDotnet.exe"),
                    Arguments = null,
#if DEBUG
                    UseShellExecute = true,
#else
                    UseShellExecute = false,
                    WindowStyle = ProcessWindowStyle.Minimized,
#endif
                    RedirectStandardOutput = false,
                    RedirectStandardError = false,
                    CreateNoWindow = true
                }

            };
            process.Start();
        }

        public void CloseSocket()
        {
            _client.Close();
        }

        public MessageHeader GetMessageSync()
        {
            MessageHeader msg = AwaitMessage();
            return msg;
        }
    }
}
