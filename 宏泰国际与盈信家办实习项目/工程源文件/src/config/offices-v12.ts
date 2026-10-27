// Prompt11 / user feedback: keep voice/captions fixed, borrow the vision sentence.
// 0.12 + 6 frames + 0.45 seconds settles the last tile at frame +24.
// Each 67-frame slot therefore keeps 43 frames (1.433s) fully still.
export const officesV12={
 start:1359,cityStarts:[1359,1426,1493],lastPhotoSettledOffset:24,
 staticFramesPerCity:43,cityChangeFrames:11,
 photoExitDelay:2,photoEntryDelay:4,tileStaggerFrames:3,photoWipeFrames:14,
 finalExitStart:1560,finalExitFrames:9,trustStart:1569,rootsStart:1652,
 titleTop:174,titleSize:72,headlineHeight:86,
 textRegion:{x:130,y:300,width:430,height:600},
 photoRegion:{x:640,y:300,width:1150,height:600},
 tiles:[{x:640,y:300,width:760,height:600},{x:1416,y:300,width:374,height:292},{x:1416,y:608,width:374,height:292}],
 caption:{left:105,right:105,bottom:58,height:55,fontSize:36},
 legal:{left:114,top:1028,width:1120,height:36,fontSize:14,lineHeight:18,opacity:.28},
} as const;
