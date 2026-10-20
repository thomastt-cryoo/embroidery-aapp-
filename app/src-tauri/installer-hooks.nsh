; Separate identity; never write extension defaults or touch Lilo registry keys.
; A standard 64 MiB LZMA dictionary improves solid compression across the
; complete offline font library. It changes packaging only, not application data.
SetCompressorDictSize 64
!define STUDIO_LICENSE "${__FILEDIR__}\..\..\LICENSE"
!define STUDIO_NOTICE "${__FILEDIR__}\..\..\NOTICE.md"
!macro NSIS_HOOK_POSTINSTALL
  SetOutPath "$INSTDIR"
  File /oname=LICENSE.txt "${STUDIO_LICENSE}"
  File /oname=NOTICE.txt "${STUDIO_NOTICE}"
  WriteRegStr HKCU "Software\Classes\Embrova.Project" "" "Embrova Project"
  WriteRegStr HKCU "Software\Classes\Embrova.Project\DefaultIcon" "" '"$INSTDIR\embrova.exe",0'
  WriteRegStr HKCU "Software\Classes\Embrova.Project\shell\open\command" "" '"$INSTDIR\embrova.exe" "%1"'
  WriteRegStr HKCU "Software\Classes\Embrova.Stitch" "" "Embrova Stitch"
  WriteRegStr HKCU "Software\Classes\Embrova.Stitch\DefaultIcon" "" '"$INSTDIR\embrova.exe",0'
  WriteRegStr HKCU "Software\Classes\Embrova.Stitch\shell\open\command" "" '"$INSTDIR\embrova.exe" "%1"'
  WriteRegStr HKCU "Software\Classes\.lilo\OpenWithProgids" "Embrova.Project" ""
  WriteRegStr HKCU "Software\Classes\.pes\OpenWithProgids" "Embrova.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.dst\OpenWithProgids" "Embrova.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.jef\OpenWithProgids" "Embrova.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.vp3\OpenWithProgids" "Embrova.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.exp\OpenWithProgids" "Embrova.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.xxx\OpenWithProgids" "Embrova.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.u01\OpenWithProgids" "Embrova.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.pec\OpenWithProgids" "Embrova.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.hus\OpenWithProgids" "Embrova.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.vip\OpenWithProgids" "Embrova.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.tbf\OpenWithProgids" "Embrova.Stitch" ""
!macroend
!macro NSIS_HOOK_POSTUNINSTALL
  DeleteRegValue HKCU "Software\Classes\.lilo\OpenWithProgids" "Embrova.Project"
  DeleteRegValue HKCU "Software\Classes\.pes\OpenWithProgids" "Embrova.Stitch"
  DeleteRegValue HKCU "Software\Classes\.dst\OpenWithProgids" "Embrova.Stitch"
  DeleteRegValue HKCU "Software\Classes\.jef\OpenWithProgids" "Embrova.Stitch"
  DeleteRegValue HKCU "Software\Classes\.vp3\OpenWithProgids" "Embrova.Stitch"
  DeleteRegValue HKCU "Software\Classes\.exp\OpenWithProgids" "Embrova.Stitch"
  DeleteRegValue HKCU "Software\Classes\.xxx\OpenWithProgids" "Embrova.Stitch"
  DeleteRegValue HKCU "Software\Classes\.u01\OpenWithProgids" "Embrova.Stitch"
  DeleteRegValue HKCU "Software\Classes\.pec\OpenWithProgids" "Embrova.Stitch"
  DeleteRegValue HKCU "Software\Classes\.hus\OpenWithProgids" "Embrova.Stitch"
  DeleteRegValue HKCU "Software\Classes\.vip\OpenWithProgids" "Embrova.Stitch"
  DeleteRegValue HKCU "Software\Classes\.tbf\OpenWithProgids" "Embrova.Stitch"
  DeleteRegKey HKCU "Software\Classes\Embrova.Project"
  DeleteRegKey HKCU "Software\Classes\Embrova.Stitch"
!macroend
