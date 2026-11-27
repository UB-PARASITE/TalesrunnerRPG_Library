//////////////////////////////////////////
//
// NOTE: This is *not* a valid shader file
//
///////////////////////////////////////////
Shader "Rhaon/Particles/Particle" {
Properties {
_MainTex ("Texture", 2D) = "white" { }
_MaskTex ("Mask", 2D) = "white" { }
_Color ("Particle Color", Color) = (1,1,1,1)
_Stencil ("Stencil ID", Float) = 0
_StencilComp ("Stencil Comparison", Float) = 8
_SrcFactor ("Src Blend Factor", Float) = 5
_DstFactor ("Dest Blend Factor", Float) = 10
_Sharpness ("Sharpness", Range(0, 0.2)) = 0.2
_CoreBlur ("Core Blur", Range(0, 1)) = 0.7
_OutsideBlur ("Outside Blur", Range(0, 1)) = 1
_PushZ ("PushZ Amounts", Range(0, 1)) = 0.1
_FlowSpd ("Flow Speed", Vector) = (0,0,0,0)
_CutLimit ("Cut Limit", Vector) = (0,0.0001,0,0)
}
SubShader {
 Tags { "IGNOREPROJECTOR" = "true" "QUEUE" = "Transparent" "RenderType" = "Transparent" }
 Pass {
  Tags { "IGNOREPROJECTOR" = "true" "QUEUE" = "Transparent" "RenderType" = "Transparent" }
  Blend Zero Zero, Zero Zero
  ZWrite Off
  Cull Off
  Stencil {
   Comp Disabled
   Pass Keep
   Fail Keep
   ZFail Keep
  }
  GpuProgramID 2816
}
}
CustomEditor "ParticleMaterial"
}