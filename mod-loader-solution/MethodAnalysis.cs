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
        public string MethodName;
        public string ClassName;
        public double TimeTaken;
    }
    public class MethodAnalysis : IDisposable
    {
        Stopwatch stopWatch = new Stopwatch();
        public MethodAnalysis()
        {
            stopWatch.Start();
        }

        public void Dispose()
        {
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
    }
}
