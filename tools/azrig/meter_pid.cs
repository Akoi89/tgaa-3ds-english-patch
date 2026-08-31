using System;
using System.Runtime.InteropServices;

[Guid("C02216F6-8C67-4B5B-9D00-D008E73E0064"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IAudioMeterInformationP { int GetPeakValue(out float peak); }

[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDeviceEnumeratorP {
  int NotImpl1();
  int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDeviceP dev);
}

[Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IMMDeviceP {
  int Activate(ref Guid iid, int clsCtx, IntPtr pars, [MarshalAs(UnmanagedType.IUnknown)] out object o);
}

[Guid("77AA99A0-1BD6-484F-8BC7-2C654C9A9B6F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IAudioSessionManager2P {
  int NotImpl1();  // GetAudioSessionControl
  int NotImpl2();  // GetSimpleAudioVolume
  int GetSessionEnumerator(out IAudioSessionEnumeratorP e);
}

[Guid("E2F5BB11-0570-40CA-ACDD-3AA01277DEE8"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IAudioSessionEnumeratorP {
  int GetCount(out int n);
  int GetSession(int i, out IAudioSessionControlP s);
}

[Guid("F4B1A599-7266-4319-A8CA-E70ACB11E8CD"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IAudioSessionControlP {
  int GetState(out int s);
  int GetDisplayName(out IntPtr p);
  int SetDisplayName(IntPtr p, IntPtr ctx);
  int GetIconPath(out IntPtr p);
  int SetIconPath(IntPtr p, IntPtr ctx);
  int GetGroupingParam(out Guid g);
  int SetGroupingParam(ref Guid g, IntPtr ctx);
  int RegisterAudioSessionNotification(IntPtr n);
  int UnregisterAudioSessionNotification(IntPtr n);
}

[Guid("bfb7ff88-7239-4fc9-8fa2-07c950be9c6d"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IAudioSessionControl2P {
  int GetState(out int s);
  int GetDisplayName(out IntPtr p);
  int SetDisplayName(IntPtr p, IntPtr ctx);
  int GetIconPath(out IntPtr p);
  int SetIconPath(IntPtr p, IntPtr ctx);
  int GetGroupingParam(out Guid g);
  int SetGroupingParam(ref Guid g, IntPtr ctx);
  int RegisterAudioSessionNotification(IntPtr n);
  int UnregisterAudioSessionNotification(IntPtr n);
  int GetSessionIdentifier(out IntPtr p);
  int GetSessionInstanceIdentifier(out IntPtr p);
  int GetProcessId(out uint pid);
}

[ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
public class MMDeviceEnumeratorP {}

public class MeterPid {
  public static float Peak(uint pid) {
    var en = (IMMDeviceEnumeratorP)(new MMDeviceEnumeratorP());
    IMMDeviceP dev; en.GetDefaultAudioEndpoint(0, 0, out dev);
    var iidMgr = typeof(IAudioSessionManager2P).GUID; object o;
    dev.Activate(ref iidMgr, 1, IntPtr.Zero, out o);
    var mgr = (IAudioSessionManager2P)o;
    IAudioSessionEnumeratorP sessions; mgr.GetSessionEnumerator(out sessions);
    int n; sessions.GetCount(out n);
    float best = -1f;
    for (int i = 0; i < n; i++) {
      IAudioSessionControlP sc; sessions.GetSession(i, out sc);
      var sc2 = (IAudioSessionControl2P)sc;
      uint p; sc2.GetProcessId(out p);
      if (p == pid) {
        var m = (IAudioMeterInformationP)sc;
        float v; m.GetPeakValue(out v);
        if (v > best) best = v;
      }
    }
    return best;   // -1 = no session found for that pid
  }
}
