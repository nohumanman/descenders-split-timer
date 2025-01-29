using ADE;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Text;

namespace ModLoaderSolution
{
    public struct Method
    {
        public string Name;
        public double TimeTaken;
    }
    public class MethodAnalysis : IDisposable
    {
        string methodName;
        Stopwatch stopWatch = new Stopwatch();
        public MethodAnalysis()
        {
            stopWatch.Start();
        }

        public void Dispose()
        {
            stopWatch.Stop();
            var stackTrace = new StackTrace();
            methodName = stackTrace.GetFrame(1)?.GetMethod()?.Name;
            HolisticMethodAnalysis.methodsCalled.Add(new Method() { Name = methodName, TimeTaken = stopWatch.Elapsed.TotalMilliseconds });
        }
    }
    public static class HolisticMethodAnalysis
    {
        public static List<Method> methodsCalled = new List<Method>();
        public static string GetCalledMethodsAsCsv()
        {
            string csv = "";
            foreach(Method method in methodsCalled)
                csv += method.Name + "," + method.TimeTaken + "\n";
            return csv;
        }
    }
}
