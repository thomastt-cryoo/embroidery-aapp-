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
  WriteRegStr HKCU "Software\Classes\EmbroideryStudio.Project" "" "Embroidery Studio Project"
  WriteRegStr HKCU "Software\Classes\EmbroideryStudio.Project\DefaultIcon" "" '"$INSTDIR\embroidery-studio.exe",0'
  WriteRegStr HKCU "Software\Classes\EmbroideryStudio.Project\shell\open\command" "" '"$INSTDIR\embroidery-studio.exe" "%1"'
  WriteRegStr HKCU "Software\Classes\EmbroideryStudio.Stitch" "" "Embroidery Studio Stitch"
  WriteRegStr HKCU "Software\Classes\EmbroideryStudio.Stitch\DefaultIcon" "" '"$INSTDIR\embroidery-studio.exe",0'
  WriteRegStr HKCU "Software\Classes\EmbroideryStudio.Stitch\shell\open\command" "" '"$INSTDIR\embroidery-studio.exe" "%1"'
  WriteRegStr HKCU "Software\Classes\.lilo\OpenWithProgids" "EmbroideryStudio.Project" ""
  WriteRegStr HKCU "Software\Classes\.pes\OpenWithProgids" "EmbroideryStudio.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.dst\OpenWithProgids" "EmbroideryStudio.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.jef\OpenWithProgids" "EmbroideryStudio.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.vp3\OpenWithProgids" "EmbroideryStudio.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.exp\OpenWithProgids" "EmbroideryStudio.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.xxx\OpenWithProgids" "EmbroideryStudio.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.u01\OpenWithProgids" "EmbroideryStudio.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.pec\OpenWithProgids" "EmbroideryStudio.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.hus\OpenWithProgids" "EmbroideryStudio.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.vip\OpenWithProgids" "EmbroideryStudio.Stitch" ""
  WriteRegStr HKCU "Software\Classes\.tbf\OpenWithProgids" "EmbroideryStudio.Stitch" ""
!macroend
!macro NSIS_HOOK_POSTUNINSTALL
  DeleteRegValue HKCU "Software\Classes\.lilo\OpenWithProgids" "EmbroideryStudio.Project"
  DeleteRegValue HKCU "Software\Classes\.pes\OpenWithProgids" "EmbroideryStudio.Stitch"
  DeleteRegValue HKCU "Software\Classes\.dst\OpenWithProgids" "EmbroideryStudio.Stitch"
  DeleteRegValue HKCU "Software\Classes\.jef\OpenWithProgids" "EmbroideryStudio.Stitch"
  DeleteRegValue HKCU "Software\Classes\.vp3\OpenWithProgids" "EmbroideryStudio.Stitch"
  DeleteRegValue HKCU "Software\Classes\.exp\OpenWithProgids" "EmbroideryStudio.Stitch"
  DeleteRegValue HKCU "Software\Classes\.xxx\OpenWithProgids" "EmbroideryStudio.Stitch"
  DeleteRegValue HKCU "Software\Classes\.u01\OpenWithProgids" "EmbroideryStudio.Stitch"
  DeleteRegValue HKCU "Software\Classes\.pec\OpenWithProgids" "EmbroideryStudio.Stitch"
  DeleteRegValue HKCU "Software\Classes\.hus\OpenWithProgids" "EmbroideryStudio.Stitch"
  DeleteRegValue HKCU "Software\Classes\.vip\OpenWithProgids" "EmbroideryStudio.Stitch"
  DeleteRegValue HKCU "Software\Classes\.tbf\OpenWithProgids" "EmbroideryStudio.Stitch"
  DeleteRegKey HKCU "Software\Classes\EmbroideryStudio.Project"
  DeleteRegKey HKCU "Software\Classes\EmbroideryStudio.Stitch"
!macroend
