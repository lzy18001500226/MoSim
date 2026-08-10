using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;
using System.Text;

public sealed class MathTypeOleFormatDescriptor
{
    public uint ClipboardFormatId { get; internal set; }
    public string ClipboardFormatName { get; internal set; }
    public int DataAspect { get; internal set; }
    public string DataAspectName { get; internal set; }
    public int LIndex { get; internal set; }
    public int Tymed { get; internal set; }
    public string TymedName { get; internal set; }
    public bool TargetDevicePresent { get; internal set; }
    public bool QueryGetDataAttempted { get; internal set; }
    public int QueryGetDataHResult { get; internal set; }
    public bool QueryGetDataAccepted { get; internal set; }
}

public sealed class MathTypeOleMathMLVariantProbe
{
    public string RequestedClipboardFormatName { get; internal set; }
    public uint RegisteredClipboardFormatId { get; internal set; }
    public int FixedHGlobalContentQueryGetDataHResult { get; internal set; }
    public bool FixedHGlobalContentQueryGetDataAccepted { get; internal set; }
    public MathTypeOleFormatDescriptor[] MatchingEnumeratedGetFormats { get; internal set; }
    public MathTypeOleFormatDescriptor[] MatchingEnumeratedSetFormats { get; internal set; }
}

public sealed class MathTypeOleFormatProbe
{
    public string EnumerationDirection { get; internal set; }
    public bool SetDataInvoked { get; internal set; }
    public bool GetDataInvoked { get; internal set; }
    public MathTypeOleFormatDescriptor[] EnumeratedGetFormats { get; internal set; }
    public MathTypeOleFormatDescriptor[] EnumeratedSetFormats { get; internal set; }
    public string SetEnumerationFailure { get; internal set; }
    public MathTypeOleMathMLVariantProbe[] MathMLVariants { get; internal set; }
}

public static class MathTypeOleData
{
    private const uint GMEM_MOVEABLE = 0x0002;
    private const uint GMEM_ZEROINIT = 0x0040;
    private const uint OLECLOSE_NOSAVE = 1;

    [DllImport("user32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern uint RegisterClipboardFormat(string lpszFormat);

    [DllImport("user32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern int GetClipboardFormatName(
        uint format,
        StringBuilder formatName,
        int maxCount
    );

    [DllImport("user32.dll", SetLastError = true)]
    private static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr GlobalAlloc(uint flags, UIntPtr bytes);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr GlobalLock(IntPtr handle);

    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool GlobalUnlock(IntPtr handle);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr GlobalFree(IntPtr handle);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern UIntPtr GlobalSize(IntPtr handle);

    [DllImport("ole32.dll")]
    private static extern void ReleaseStgMedium(ref STGMEDIUM medium);

    [ComImport]
    [Guid("00000112-0000-0000-C000-000000000046")]
    [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    private interface IOleObject
    {
        [PreserveSig]
        int SetClientSite(IntPtr clientSite);

        [PreserveSig]
        int GetClientSite(out IntPtr clientSite);

        [PreserveSig]
        int SetHostNames(
            [MarshalAs(UnmanagedType.LPWStr)] string containerApp,
            [MarshalAs(UnmanagedType.LPWStr)] string containerObject
        );

        [PreserveSig]
        int Close(uint saveOption);
    }

    public static uint WindowProcessId(long hwnd)
    {
        uint processId;
        GetWindowThreadProcessId(new IntPtr(hwnd), out processId);
        return processId;
    }

    public static MathTypeOleFormatProbe ProbeMathMLFormats(object oleFormatObject)
    {
        if (oleFormatObject == null)
        {
            throw new ArgumentNullException("oleFormatObject");
        }

        IDataObject dataObject = QueryInterface<IDataObject>(oleFormatObject);
        MathTypeOleFormatDescriptor[] getFormats = EnumerateFormats(
            dataObject,
            DATADIR.DATADIR_GET,
            true
        );
        MathTypeOleFormatDescriptor[] setFormats =
            new MathTypeOleFormatDescriptor[0];
        string setEnumerationFailure = null;
        try
        {
            setFormats = EnumerateFormats(
                dataObject,
                DATADIR.DATADIR_SET,
                false
            );
        }
        catch (Exception exception)
        {
            setEnumerationFailure = exception.GetType().FullName + ": " +
                exception.Message;
        }
        string[] candidateNames = new string[]
        {
            "MathML Presentation",
            "MathML",
            "application/mathml+xml",
        };
        MathTypeOleMathMLVariantProbe[] candidates =
            new MathTypeOleMathMLVariantProbe[candidateNames.Length];

        for (int index = 0; index < candidateNames.Length; index++)
        {
            string candidateName = candidateNames[index];
            uint formatId = RegisteredClipboardFormat(candidateName);
            FORMATETC request = CreateFormat(
                formatId,
                DVASPECT.DVASPECT_CONTENT,
                -1,
                TYMED.TYMED_HGLOBAL
            );
            int queryResult = dataObject.QueryGetData(ref request);
            List<MathTypeOleFormatDescriptor> matchingGetFormats =
                new List<MathTypeOleFormatDescriptor>();
            foreach (MathTypeOleFormatDescriptor format in getFormats)
            {
                if (format.ClipboardFormatId == formatId)
                {
                    matchingGetFormats.Add(format);
                }
            }
            List<MathTypeOleFormatDescriptor> matchingSetFormats =
                new List<MathTypeOleFormatDescriptor>();
            foreach (MathTypeOleFormatDescriptor format in setFormats)
            {
                if (format.ClipboardFormatId == formatId)
                {
                    matchingSetFormats.Add(format);
                }
            }

            candidates[index] = new MathTypeOleMathMLVariantProbe()
            {
                RequestedClipboardFormatName = candidateName,
                RegisteredClipboardFormatId = formatId,
                FixedHGlobalContentQueryGetDataHResult = queryResult,
                FixedHGlobalContentQueryGetDataAccepted = queryResult == 0,
                MatchingEnumeratedGetFormats = matchingGetFormats.ToArray(),
                MatchingEnumeratedSetFormats = matchingSetFormats.ToArray(),
            };
        }

        return new MathTypeOleFormatProbe()
        {
            EnumerationDirection = "DATADIR_GET,DATADIR_SET",
            SetDataInvoked = false,
            GetDataInvoked = false,
            EnumeratedGetFormats = getFormats,
            EnumeratedSetFormats = setFormats,
            SetEnumerationFailure = setEnumerationFailure,
            MathMLVariants = candidates,
        };
    }

    public static string BuildPresentationMathMLPayload(string mathml)
    {
        if (String.IsNullOrWhiteSpace(mathml))
        {
            throw new ArgumentException("MathML payload is empty", "mathml");
        }

        string value = mathml.Trim();
        if (!value.StartsWith("<math", StringComparison.Ordinal))
        {
            throw new ArgumentException("MathML payload must start with a math element", "mathml");
        }
        // MathType's IDataObject accepts the MathML document element itself.
        // Wrapping it in HTML caused SetData to fail in the direct OLE route.
        return value;
    }

    public static void SetPresentationMathML(object oleFormatObject, string mathml)
    {
        if (oleFormatObject == null)
        {
            throw new ArgumentNullException("oleFormatObject");
        }

        IDataObject dataObject = QueryInterface<IDataObject>(oleFormatObject);
        FORMATETC format = PresentationMathMLFormat();
        int queryResult = dataObject.QueryGetData(ref format);
        if (queryResult != 0)
        {
            throw new COMException(
                "MathType OLE object does not accept MathML",
                queryResult
            );
        }

        byte[] payload = Encoding.UTF8.GetBytes(
            BuildPresentationMathMLPayload(mathml) + "\0"
        );
        IntPtr global = GlobalAlloc(
            GMEM_MOVEABLE | GMEM_ZEROINIT,
            new UIntPtr((uint)payload.Length)
        );
        if (global == IntPtr.Zero)
        {
            throw new OutOfMemoryException("GlobalAlloc failed for MathML payload");
        }

        bool ownershipTransferred = false;
        try
        {
            IntPtr target = GlobalLock(global);
            if (target == IntPtr.Zero)
            {
                throw new COMException(
                    "GlobalLock failed for MathML payload",
                    Marshal.GetHRForLastWin32Error()
                );
            }
            try
            {
                Marshal.Copy(payload, 0, target, payload.Length);
            }
            finally
            {
                GlobalUnlock(global);
            }

            STGMEDIUM medium = new STGMEDIUM();
            medium.tymed = TYMED.TYMED_HGLOBAL;
            medium.unionmember = global;
            medium.pUnkForRelease = null;
            dataObject.SetData(ref format, ref medium, true);
            ownershipTransferred = true;
        }
        finally
        {
            if (!ownershipTransferred)
            {
                GlobalFree(global);
            }
        }
    }

    public static string GetPresentationMathML(object oleFormatObject)
    {
        if (oleFormatObject == null)
        {
            throw new ArgumentNullException("oleFormatObject");
        }

        IDataObject dataObject = QueryInterface<IDataObject>(oleFormatObject);
        FORMATETC format = PresentationMathMLFormat();
        STGMEDIUM medium = new STGMEDIUM();
        try
        {
            dataObject.GetData(ref format, out medium);
            if (medium.tymed != TYMED.TYMED_HGLOBAL || medium.unionmember == IntPtr.Zero)
            {
                throw new COMException("MathType returned a non-HGLOBAL MathML payload");
            }

            IntPtr source = GlobalLock(medium.unionmember);
            if (source == IntPtr.Zero)
            {
                throw new COMException(
                    "GlobalLock failed for MathML readback",
                    Marshal.GetHRForLastWin32Error()
                );
            }
            try
            {
                ulong rawSize = GlobalSize(medium.unionmember).ToUInt64();
                if (rawSize == 0 || rawSize > Int32.MaxValue)
                {
                    throw new COMException("MathType returned an invalid MathML payload size");
                }
                byte[] bytes = new byte[(int)rawSize];
                Marshal.Copy(source, bytes, 0, bytes.Length);
                int terminator = Array.IndexOf(bytes, (byte)0);
                int length = terminator >= 0 ? terminator : bytes.Length;
                return Encoding.UTF8.GetString(bytes, 0, length);
            }
            finally
            {
                GlobalUnlock(medium.unionmember);
            }
        }
        finally
        {
            if (medium.unionmember != IntPtr.Zero)
            {
                ReleaseStgMedium(ref medium);
            }
        }
    }

    public static void CloseWithoutSave(object oleFormatObject)
    {
        if (oleFormatObject == null)
        {
            return;
        }

        IOleObject oleObject = QueryInterface<IOleObject>(oleFormatObject);
        int closeResult = oleObject.Close(OLECLOSE_NOSAVE);
        if (closeResult != 0)
        {
            throw new COMException("MathType IOleObject.Close failed", closeResult);
        }
    }

    private static FORMATETC PresentationMathMLFormat()
    {
        return CreateFormat(
            RegisteredClipboardFormat("MathML Presentation"),
            DVASPECT.DVASPECT_CONTENT,
            -1,
            TYMED.TYMED_HGLOBAL
        );
    }

    private static MathTypeOleFormatDescriptor[] EnumerateFormats(
        IDataObject dataObject,
        DATADIR direction,
        bool queryGetData
    )
    {
        IEnumFORMATETC enumerator = dataObject.EnumFormatEtc(direction);
        if (enumerator == null)
        {
            throw new COMException(
                "MathType IDataObject returned no " + direction.ToString() +
                " format enumerator"
            );
        }

        List<MathTypeOleFormatDescriptor> formats =
            new List<MathTypeOleFormatDescriptor>();
        try
        {
            while (true)
            {
                FORMATETC[] values = new FORMATETC[1];
                int[] fetched = new int[1];
                int result = enumerator.Next(1, values, fetched);
                if (result != 0 && result != 1)
                {
                    throw new COMException(
                        "MathType IEnumFORMATETC.Next failed",
                        result
                    );
                }
                if (fetched[0] == 0)
                {
                    break;
                }

                FORMATETC format = values[0];
                formats.Add(DescribeFormat(
                    dataObject,
                    ref format,
                    queryGetData
                ));
                if (result == 1)
                {
                    break;
                }
            }
        }
        finally
        {
            if (Marshal.IsComObject(enumerator))
            {
                Marshal.ReleaseComObject(enumerator);
            }
        }
        return formats.ToArray();
    }

    private static MathTypeOleFormatDescriptor DescribeFormat(
        IDataObject dataObject,
        ref FORMATETC format,
        bool queryGetData
    )
    {
        uint formatId = unchecked((ushort)format.cfFormat);
        int queryResult = 0;
        if (queryGetData)
        {
            queryResult = dataObject.QueryGetData(ref format);
        }
        return new MathTypeOleFormatDescriptor()
        {
            ClipboardFormatId = formatId,
            ClipboardFormatName = ClipboardFormatName(formatId),
            DataAspect = (int)format.dwAspect,
            DataAspectName = format.dwAspect.ToString(),
            LIndex = format.lindex,
            Tymed = (int)format.tymed,
            TymedName = format.tymed.ToString(),
            TargetDevicePresent = format.ptd != IntPtr.Zero,
            QueryGetDataAttempted = queryGetData,
            QueryGetDataHResult = queryResult,
            QueryGetDataAccepted = queryGetData && queryResult == 0,
        };
    }

    private static uint RegisteredClipboardFormat(string formatName)
    {
        uint formatId = RegisterClipboardFormat(formatName);
        if (formatId == 0)
        {
            throw new COMException(
                "RegisterClipboardFormat failed for " + formatName,
                Marshal.GetHRForLastWin32Error()
            );
        }
        return formatId;
    }

    private static FORMATETC CreateFormat(
        uint formatId,
        DVASPECT aspect,
        int lindex,
        TYMED tymed
    )
    {
        FORMATETC format = new FORMATETC();
        format.cfFormat = unchecked((short)formatId);
        format.dwAspect = aspect;
        format.lindex = lindex;
        format.ptd = IntPtr.Zero;
        format.tymed = tymed;
        return format;
    }

    private static string ClipboardFormatName(uint formatId)
    {
        StringBuilder name = new StringBuilder(256);
        int count = GetClipboardFormatName(formatId, name, name.Capacity);
        if (count > 0)
        {
            return name.ToString();
        }
        return "CF_" + formatId.ToString();
    }

    private static T QueryInterface<T>(object comObject) where T : class
    {
        IntPtr unknown = Marshal.GetIUnknownForObject(comObject);
        try
        {
            return (T)Marshal.GetTypedObjectForIUnknown(unknown, typeof(T));
        }
        finally
        {
            Marshal.Release(unknown);
        }
    }
}
