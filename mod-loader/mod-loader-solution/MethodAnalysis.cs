using ADE;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;

namespace ModLoaderSolution
{
    public struct Method
    {
        public string MethodName;
        public string ClassName;
        public double TimeTaken;
    }
    public class MethodAnalysis : IDisposable
    {
        Stopwatch stopWatch = new Stopwatch();
        public MethodAnalysis()
        {
            if (NetClient.debugState == DebugType.RELEASE)
                return;
            stopWatch.Start();
        }

        public void Dispose()
        {
            if (NetClient.debugState == DebugType.RELEASE)
                return;
            stopWatch.Stop();
            StackTrace stackTrace = new StackTrace();
            MethodBase method = stackTrace.GetFrame(1)?.GetMethod();
            HolisticMethodAnalysis.methodsCalled.Add(
                new Method() {
                    MethodName = method.Name,
                    ClassName = method.DeclaringType.Name,
                    TimeTaken = stopWatch.Elapsed.TotalMilliseconds
                }
            );
        }
    }
    public static class HolisticMethodAnalysis
    {
        public static List<Method> methodsCalled = new List<Method>();
        public static string GetCalledMethodsAsCsv()
        {
            string csv = "";
            foreach(Method method in methodsCalled)
                csv += method.MethodName + "," + method.ClassName + "," + method.TimeTaken + "\n";
            return csv;
        }
        public static void WriteCalledMethodsToCsv(string filepath)
        {
            // log to LocalLow > RageSuid > Descenders > checkpoint-logs.txt
            string path = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData) + "Low\\RageSquid\\Descenders\\checkpoint-logs.txt";
            StreamWriter writer = new StreamWriter(filepath, true);
            writer.Write(GetCalledMethodsAsCsv());
            writer.Close();
        }
    }
}
