﻿using SkylinesPythonShared;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;

namespace PythonConsole
{
    public class PythonConsole
    {
        private static PythonConsole _instance;
        public static PythonConsole Instsance
        {
            get
            {
                if (_instance == null)
                    _instance = new PythonConsole();
                return _instance;
            }
        }

        private TcpClient _client;
        private string _scheduledScript;
        private bool _isRunning;
        private bool _isClientReady;

        public bool CanExecuteScript => !_isRunning && _isClientReady;
        public PythonConsole()
        {
            try
            {
                _client = TcpClient.CreateClient();
                _isClientReady = true;
            } catch
            {  }
            
        }

        public void ScheduleExecution(string script)
        {
            _scheduledScript = script;
        }

        public void SimulationStep()
        {
            try
            {
                if (!_isClientReady)
                {
                    _client = TcpClient.CreateClient();
                    _isClientReady = true;
                }
            } catch { }
            
            try
            {
                if (_scheduledScript != null && !_isRunning && _isClientReady)
                {
                    RunScriptMessage msg = new RunScriptMessage();
                    msg.script = _scheduledScript;
                    _scheduledScript = null;
                    var timer = new Stopwatch();
                    timer.Start();
                    _client.SendMessage(msg, "s_script_run");
                    _isRunning = true;
                    while (_isRunning)
                    {
                        MessageHeader header = _client.GetMessage();
                        switch (header.messageType)
                        {
                            case "c_output_message": UIWindow.Instance.Log((string)header.payload); break;
                            case "c_exception":
                                UIWindow.Instance.Log("Exception: " + (string)header.payload + "\n");
                                _isRunning = false; break;
                            case "c_failed_to_compile":
                                UIWindow.Instance.Log("Failed to compile:" + (string)header.payload + "\n");
                                _isRunning = false; break;
                            case "c_script_end":
                                timer.Stop();
                                UIWindow.Instance.Log("Execution took " + timer.ElapsedMilliseconds + " ms\n");
                                _isRunning = false; break;
                            default:
                                if (header.messageType.StartsWith("c_callfunc_"))
                                {
                                    HandleCall.HandleAPICall(header.payload, header.messageType, _client);
                                }
                                break;
                        }
                    }
                }
            } finally
            {
                _isRunning = false;
            }
            
        }
    }
}
