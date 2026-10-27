// Prompt08 optical fitting. Original JPEG RGB files are unchanged; the SVG
// stencil only clips edge-connected light background, keeping enclosed whites.
// opticalScale is relative to fitting the effective ink bounds inside 96x54.
export const logoGridV12 = {
 cols:5, rows:5, cellWidth:128, cellHeight:78, gap:16,
 width:704, height:454, top:300, premiumLeft:1010, commissionLeft:920,
 safeWidth:96, safeHeight:54, settledOpacity:.82, tileColor:'#F4EEE2',
 premiumStartFrame:431, commissionStartFrame:525, clientsStartFrame:609,
 shiftFrames:23, rowAppendStartFrame:528, rowStaggerFrames:2, fadeFrames:6,
} as const;
export const logoOpticalV12 = [
  {
    "id": "hk-01",
    "name": "中國太平洋保險",
    "file": "stills/v12/provider-hk-01.jpg",
    "role": "insurance",
    "slot": 0,
    "row": 0,
    "col": 0,
    "sourceWidth": 330,
    "sourceHeight": 235,
    "ink": [
      26,
      82,
      309,
      179
    ],
    "opticalScale": 0.95833333,
    "displayInkWidth": 92.0,
    "displayInkHeight": 31.53357,
    "target": [
      "width",
      92
    ],
    "sourceSha256": "cc06286e11f5edfb041dbda78959b2d5c0db0d289b8bb77d34750850f46cb689"
  },
  {
    "id": "hk-02",
    "name": "保誠",
    "file": "stills/v12/provider-hk-02.jpg",
    "role": "insurance",
    "slot": 1,
    "row": 0,
    "col": 1,
    "sourceWidth": 329,
    "sourceHeight": 235,
    "ink": [
      47,
      46,
      278,
      188
    ],
    "opticalScale": 0.74074074,
    "displayInkWidth": 65.07042,
    "displayInkHeight": 40.0,
    "target": [
      "height",
      40
    ],
    "sourceSha256": "441c5ef9be5b0b69ac08bbd538a7d81a9a3c6ef07d20b162e304db8ae52fa879"
  },
  {
    "id": "hk-03",
    "name": "Sun Life 永明",
    "file": "stills/v12/provider-hk-03.jpg",
    "role": "insurance",
    "slot": 2,
    "row": 0,
    "col": 2,
    "sourceWidth": 329,
    "sourceHeight": 235,
    "ink": [
      8,
      52,
      322,
      181
    ],
    "opticalScale": 0.88,
    "displayInkWidth": 84.48,
    "displayInkHeight": 34.70675,
    "target": [
      "width",
      84.48
    ],
    "sourceSha256": "480c25dad57073d525e8dbaf06ea5f18101affda209641b0044e280eee98d7ea"
  },
  {
    "id": "hk-04",
    "name": "CTF Life 周大福人壽",
    "file": "stills/v12/provider-hk-04.jpg",
    "role": "insurance",
    "slot": 3,
    "row": 0,
    "col": 3,
    "sourceWidth": 329,
    "sourceHeight": 235,
    "ink": [
      57,
      66,
      280,
      169
    ],
    "opticalScale": 0.88,
    "displayInkWidth": 84.48,
    "displayInkHeight": 39.01991,
    "target": [
      "width",
      84.48
    ],
    "sourceSha256": "6bcfd928fa44ca75b8bc958d2b10e6a08d08d5d9506bd104c05aafee35e00193"
  },
  {
    "id": "hk-05",
    "name": "CHUBB",
    "file": "stills/v12/provider-hk-05.jpg",
    "role": "insurance",
    "slot": 4,
    "row": 0,
    "col": 4,
    "sourceWidth": 330,
    "sourceHeight": 235,
    "ink": [
      25,
      102,
      307,
      131
    ],
    "opticalScale": 0.88,
    "displayInkWidth": 84.48,
    "displayInkHeight": 8.68766,
    "target": [
      "width",
      84.48
    ],
    "sourceSha256": "aa31caafe7aa1ba53f9fce6a94d8d0a2072526bac0ef91de41da52319beb56c8"
  },
  {
    "id": "hk-06",
    "name": "AIA 友邦",
    "file": "stills/v12/provider-hk-06.jpg",
    "role": "insurance",
    "slot": 5,
    "row": 1,
    "col": 0,
    "sourceWidth": 329,
    "sourceHeight": 235,
    "ink": [
      91,
      39,
      244,
      201
    ],
    "opticalScale": 0.7,
    "displayInkWidth": 35.7,
    "displayInkHeight": 37.8,
    "target": [
      "height",
      37.8
    ],
    "sourceSha256": "da03499c938a8a21deaba808a13329d81104f4aea3970f5d5e148a33b9da1fe3"
  },
  {
    "id": "hk-08",
    "name": "宏利 Manulife",
    "file": "stills/v12/provider-hk-08.jpg",
    "role": "insurance",
    "slot": 6,
    "row": 1,
    "col": 1,
    "sourceWidth": 330,
    "sourceHeight": 235,
    "ink": [
      28,
      74,
      298,
      161
    ],
    "opticalScale": 0.88,
    "displayInkWidth": 84.48,
    "displayInkHeight": 27.22133,
    "target": [
      "width",
      84.48
    ],
    "sourceSha256": "c0d644ba8d035d2794babebf5efd614f4f1330cc53f8b601f297ba4c2d78b102"
  },
  {
    "id": "hk-09",
    "name": "AXA 安盛",
    "file": "stills/v12/provider-hk-09.jpg",
    "role": "insurance",
    "slot": 7,
    "row": 1,
    "col": 2,
    "sourceWidth": 329,
    "sourceHeight": 235,
    "ink": [
      96,
      46,
      237,
      188
    ],
    "opticalScale": 0.7,
    "displayInkWidth": 37.5338,
    "displayInkHeight": 37.8,
    "target": [
      "height",
      37.8
    ],
    "sourceSha256": "e122b7dd961d28a7d4147acafc0d685fbf9a79f5ee1a9946003988043fe19704"
  },
  {
    "id": "hk-10",
    "name": "中銀人壽",
    "file": "stills/v12/provider-hk-10.jpg",
    "role": "insurance",
    "slot": 8,
    "row": 1,
    "col": 3,
    "sourceWidth": 329,
    "sourceHeight": 235,
    "ink": [
      18,
      70,
      300,
      164
    ],
    "opticalScale": 0.9375,
    "displayInkWidth": 90.0,
    "displayInkHeight": 30.0,
    "target": [
      "width",
      90
    ],
    "sourceSha256": "64b21e35c4ae4fbc76542f1d0e278c03d0235abe534f35cf94156f97909ac359"
  },
  {
    "id": "hk-11",
    "name": "中國人壽（海外）",
    "file": "stills/v12/provider-hk-11.jpg",
    "role": "insurance",
    "slot": 9,
    "row": 1,
    "col": 4,
    "sourceWidth": 329,
    "sourceHeight": 235,
    "ink": [
      37,
      30,
      290,
      202
    ],
    "opticalScale": 0.78,
    "displayInkWidth": 61.95558,
    "displayInkHeight": 42.12,
    "target": [
      "height",
      42.12
    ],
    "sourceSha256": "1a29eca09b314644843437b7f702f2b298fe5772af06b865707c065de7dc96cd"
  },
  {
    "id": "hk-12",
    "name": "中國太平",
    "file": "stills/v12/provider-hk-12.jpg",
    "role": "insurance",
    "slot": 10,
    "row": 2,
    "col": 0,
    "sourceWidth": 330,
    "sourceHeight": 235,
    "ink": [
      81,
      15,
      259,
      211
    ],
    "opticalScale": 0.78,
    "displayInkWidth": 38.25184,
    "displayInkHeight": 42.12,
    "target": [
      "height",
      42.12
    ],
    "sourceSha256": "e1d1fb37039325d5af6656d3c179450a867f1e6556a3d57ef5211be3b19f102f"
  },
  {
    "id": "hk-13",
    "name": "Friends Provident International",
    "file": "stills/v12/provider-hk-13.jpg",
    "role": "insurance",
    "slot": 11,
    "row": 2,
    "col": 1,
    "sourceWidth": 329,
    "sourceHeight": 235,
    "ink": [
      32,
      53,
      299,
      176
    ],
    "opticalScale": 0.94791667,
    "displayInkWidth": 91.0,
    "displayInkHeight": 41.92135,
    "target": [
      "width",
      91
    ],
    "sourceSha256": "167856d9bd0af38bce1aec08139da183ec86790714882bd4cc26678338a4523d"
  },
  {
    "id": "hk-14",
    "name": "恒安標準人壽",
    "file": "stills/v12/provider-hk-14.jpg",
    "role": "insurance",
    "slot": 12,
    "row": 2,
    "col": 2,
    "sourceWidth": 329,
    "sourceHeight": 235,
    "ink": [
      25,
      60,
      312,
      156
    ],
    "opticalScale": 0.94791667,
    "displayInkWidth": 91.0,
    "displayInkHeight": 30.43902,
    "target": [
      "width",
      91
    ],
    "sourceSha256": "dd6b9073ff431d9f702e69032d33d9e4380a8cd41ac8bef267b7b4280c826ae6"
  },
  {
    "id": "hk-15",
    "name": "萬通保險 YF Life",
    "file": "stills/v12/provider-hk-15.jpg",
    "role": "insurance",
    "slot": 13,
    "row": 2,
    "col": 3,
    "sourceWidth": 330,
    "sourceHeight": 235,
    "ink": [
      31,
      61,
      301,
      177
    ],
    "opticalScale": 0.88,
    "displayInkWidth": 84.48,
    "displayInkHeight": 36.29511,
    "target": [
      "width",
      84.48
    ],
    "sourceSha256": "ba789c38e84150a31cacbf349482e94fdb8c06c801ce4bc1464f53ecafea2cfb"
  },
  {
    "id": "hk-16",
    "name": "立橋人壽",
    "file": "stills/v12/provider-hk-16.jpg",
    "role": "insurance",
    "slot": 14,
    "row": 2,
    "col": 4,
    "sourceWidth": 329,
    "sourceHeight": 235,
    "ink": [
      13,
      81,
      317,
      161
    ],
    "opticalScale": 0.9375,
    "displayInkWidth": 90.0,
    "displayInkHeight": 23.68421,
    "target": [
      "width",
      90
    ],
    "sourceSha256": "f04aaa52d684397b911dd20981d520517422e6f63f3eb5cf34e8fef3c7b9f41d"
  },
  {
    "id": "hk-17",
    "name": "GENERALI 忠利",
    "file": "stills/v12/provider-hk-17.jpg",
    "role": "insurance",
    "slot": 15,
    "row": 3,
    "col": 0,
    "sourceWidth": 329,
    "sourceHeight": 235,
    "ink": [
      78,
      47,
      248,
      185
    ],
    "opticalScale": 0.74074074,
    "displayInkWidth": 49.27536,
    "displayInkHeight": 40.0,
    "target": [
      "height",
      40
    ],
    "sourceSha256": "88609e77eb953f291cc192b54919aee04530aa72fea6af28f50e46103fc95589"
  },
  {
    "id": "hk-18",
    "name": "富衛 FWD",
    "file": "stills/v12/provider-hk-18.jpg",
    "role": "insurance",
    "slot": 16,
    "row": 3,
    "col": 1,
    "sourceWidth": 329,
    "sourceHeight": 235,
    "ink": [
      62,
      63,
      265,
      175
    ],
    "opticalScale": 0.8125,
    "displayInkWidth": 78.0,
    "displayInkHeight": 43.03448,
    "target": [
      "width",
      78
    ],
    "sourceSha256": "dc28920957e6bdd3e335bb0be3908495c408d555b694154afb86d63cb7fad148"
  },
  {
    "id": "hk-20",
    "name": "太平洋人壽 PACIFIC LIFE",
    "file": "stills/v12/provider-hk-20.jpg",
    "role": "insurance",
    "slot": 17,
    "row": 3,
    "col": 2,
    "sourceWidth": 329,
    "sourceHeight": 235,
    "ink": [
      14,
      78,
      321,
      154
    ],
    "opticalScale": 0.9375,
    "displayInkWidth": 90.0,
    "displayInkHeight": 22.28013,
    "target": [
      "width",
      90
    ],
    "sourceSha256": "0c1291f39e29c0fc71927247c9641c9961ec2b9b2e3aee02680a2262df98e3be"
  },
  {
    "id": "hk-22",
    "name": "Principal 信安",
    "file": "stills/v12/provider-hk-22.jpg",
    "role": "insurance",
    "slot": 18,
    "row": 3,
    "col": 3,
    "sourceWidth": 330,
    "sourceHeight": 235,
    "ink": [
      29,
      88,
      301,
      148
    ],
    "opticalScale": 0.9375,
    "displayInkWidth": 90.0,
    "displayInkHeight": 19.85294,
    "target": [
      "width",
      90
    ],
    "sourceSha256": "768bed1eb3782170d9338b66adf30d0681527ad456c440744be768780cb7d229"
  },
  {
    "id": "hk-24",
    "name": "blue",
    "file": "stills/v12/provider-hk-24.jpg",
    "role": "insurance",
    "slot": 19,
    "row": 3,
    "col": 4,
    "sourceWidth": 329,
    "sourceHeight": 235,
    "ink": [
      56,
      56,
      293,
      184
    ],
    "opticalScale": 0.8125,
    "displayInkWidth": 78.0,
    "displayInkHeight": 42.12658,
    "target": [
      "width",
      78
    ],
    "sourceSha256": "ab332e813543e3aaf143d8c27dc78196181708e3dad53eda79f12d4d75e7e11e"
  },
  {
    "id": "hk-25",
    "name": "ZURICH 蘇黎世",
    "file": "stills/v12/provider-hk-25.jpg",
    "role": "insurance",
    "slot": 20,
    "row": 4,
    "col": 0,
    "sourceWidth": 329,
    "sourceHeight": 235,
    "ink": [
      87,
      37,
      266,
      194
    ],
    "opticalScale": 0.7,
    "displayInkWidth": 43.09682,
    "displayInkHeight": 37.8,
    "target": [
      "height",
      37.8
    ],
    "sourceSha256": "7b5e81c8b759c199de07f7b6214a65e34766607f4de404e69df1476f8272791a"
  },
  {
    "id": "hk-26",
    "name": "MSIG 三井住友",
    "file": "stills/v12/provider-hk-26.jpg",
    "role": "insurance",
    "slot": 21,
    "row": 4,
    "col": 1,
    "sourceWidth": 330,
    "sourceHeight": 235,
    "ink": [
      106,
      13,
      237,
      210
    ],
    "opticalScale": 0.78,
    "displayInkWidth": 28.00873,
    "displayInkHeight": 42.12,
    "target": [
      "height",
      42.12
    ],
    "sourceSha256": "0a8cf09f0d75a0cd6a001f50ff9107ebdb8bac5302fa2e3ffe9d481ab2551933"
  },
  {
    "id": "hk-27",
    "name": "Bupa 保柏",
    "file": "stills/v12/provider-hk-27.jpg",
    "role": "insurance",
    "slot": 22,
    "row": 4,
    "col": 2,
    "sourceWidth": 329,
    "sourceHeight": 235,
    "ink": [
      90,
      39,
      248,
      193
    ],
    "opticalScale": 0.7,
    "displayInkWidth": 38.78182,
    "displayInkHeight": 37.8,
    "target": [
      "height",
      37.8
    ],
    "sourceSha256": "ea923068381a078d7abe238646d1e2fe7a7ae17fa913efc436884d912e2b3b0b"
  },
  {
    "id": "bank-minsheng",
    "name": "中國民生銀行",
    "file": "stills/v12/bank-minsheng.jpg",
    "role": "bank",
    "slot": 23,
    "row": 4,
    "col": 3,
    "sourceWidth": 779,
    "sourceHeight": 171,
    "ink": [
      11,
      19,
      747,
      149
    ],
    "opticalScale": 0.88,
    "displayInkWidth": 84.48,
    "displayInkHeight": 14.92174,
    "target": [
      "width",
      84.48
    ],
    "sourceSha256": "ea41c909116b470d8c3b10298cea81e6810c3444cd2fc3919b36b3397682c7bc"
  },
  {
    "id": "bank-shanghai",
    "name": "上海商業銀行",
    "file": "stills/v12/bank-shanghai.jpg",
    "role": "bank",
    "slot": 24,
    "row": 4,
    "col": 4,
    "sourceWidth": 850,
    "sourceHeight": 250,
    "ink": [
      16,
      22,
      832,
      174
    ],
    "opticalScale": 0.88,
    "displayInkWidth": 84.48,
    "displayInkHeight": 15.73647,
    "target": [
      "width",
      84.48
    ],
    "sourceSha256": "006b916abb2466750f26d4cafb841d6a5a9795c621b3b61dd78574092b190424"
  }
] as const;
