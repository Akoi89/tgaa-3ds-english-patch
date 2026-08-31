using System; using System.Runtime.InteropServices;
[Guid("C02216F6-8C67-4B5B-9D00-D008E73E0064"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IAudioMeterInformation2 { int GetPeakValue(out float peak); }
[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDeviceEnumerator2 { int NotImpl1(); int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice2 dev); }
[Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDevice2 { int Activate(ref Guid iid, int clsCtx, IntPtr pars, [MarshalAs(UnmanagedType.IUnknown)] out object o); }
[ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
public class MMDeviceEnumerator2 {}
public class Meter2 {
  public static float Peak() {
    var en = (IMMDeviceEnumerator2)(new MMDeviceEnumerator2());
    IMMDevice2 dev; en.GetDefaultAudioEndpoint(0, 0, out dev);
    var iid = typeof(IAudioMeterInformation2).GUID; object o;
    dev.Activate(ref iid, 1, IntPtr.Zero, out o);
    float p; ((IAudioMeterInformation2)o).GetPeakValue(out p);
    return p;
  }
}