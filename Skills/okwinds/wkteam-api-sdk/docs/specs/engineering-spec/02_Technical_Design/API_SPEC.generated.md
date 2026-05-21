# API Spec (Generated from Offline Docs)

Generated at: `2026-02-10T05:09:45.090Z`

本文件由离线文档自动提取生成，用于：
- 提供 SDK 实现所需的 **endpoint 索引**（method/path/参数/返回）
- 为“覆盖性复查”提供机器可核验的清单

权威来源仍为 `docs/api/` 中的接口说明文档；当自动解析缺失时，以原文档为准并在后续手工补齐解析规则。

Catalog JSON: `docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json`

## Module: `biao-qian`

| operationId | title | method | path | doc |
|---|---|---|---|---|
| `biao_qian_addContactLabel` | 创建标签 | `POST` | `/addContactLabel` | `docs/api/api-wen-dang2/biao-qian/addContactLabel.md` |
| `biao_qian_delContactLabel` | 删除联系人标签 | `POST` | `/delContactLabel` | `docs/api/api-wen-dang2/biao-qian/delContactLabel.md` |
| `biao_qian_getContactLabelList` | 获取标签列表 | `POST` | `/getContactLabelList` | `docs/api/api-wen-dang2/biao-qian/getContactLabelList.md` |
| `biao_qian_modifyContactLabel` | 修改联系人标签 | `POST` | `/modifyContactLabel` | `docs/api/api-wen-dang2/biao-qian/modifyContactLabel.md` |

## Module: `deng-lu`

| operationId | title | method | path | doc |
|---|---|---|---|---|
| `deng_lu_deng_lu_wei_kong_ping_tai_di_yi_bu` | 登录E云平台（第一步） | `POST` | `/member/login` | `docs/api/api-wen-dang2/deng-lu/deng-lu-wei-kong-ping-tai-di-yi-bu.md` |
| `deng_lu_er_ci_deng_lu` | 弹框登录 | `POST` | `/secondLogin` | `docs/api/api-wen-dang2/deng-lu/er-ci-deng-lu.md` |
| `deng_lu_huo_qu_wei_xin_er_wei_ma2` | 获取二维码（第二步-方式1） | `POST` | `/iPadLogin` | `docs/api/api-wen-dang2/deng-lu/huo-qu-wei-xin-er-wei-ma2.md` |
| `deng_lu_initFriendList` | 初始化通讯录列表 | `POST` | `/initAddressList` | `docs/api/api-wen-dang2/deng-lu/initFriendList.md` |
| `deng_lu_queryFriendList` | 获取通讯录列表 | `POST` | `/getAddressList` | `docs/api/api-wen-dang2/deng-lu/queryFriendList.md` |
| `deng_lu_zhang_hao_mi_ma_deng_lu` | 账号密码登录 | `POST` | `/loginByAccountAndPassword` | `docs/api/api-wen-dang2/deng-lu/zhang-hao-mi-ma-deng-lu.md` |
| `deng_lu_zhi_xing_wei_xin_deng_lu` | 执行微信登录（第三步） | `POST` | `/getIPadLoginInfo` | `docs/api/api-wen-dang2/deng-lu/zhi-xing-wei-xin-deng-lu.md` |

## Module: `hao-you-cao-zuo`

| operationId | title | method | path | doc |
|---|---|---|---|---|
| `hao_you_cao_zuo_acceptUser` | 同意添加好友 | `POST` | `/acceptUser` | `docs/api/api-wen-dang2/hao-you-cao-zuo/acceptUser.md` |
| `hao_you_cao_zuo_addFriend` | 添加好友 | `POST` | `/addUser` | `docs/api/api-wen-dang2/hao-you-cao-zuo/addFriend.md` |
| `hao_you_cao_zuo_checkZombie` | 检测好友状态 | `POST` | `/checkZombie` | `docs/api/api-wen-dang2/hao-you-cao-zuo/checkZombie.md` |
| `hao_you_cao_zuo_getImAddressList` | 获取企微联系人列表 | `POST` | `/getImAddressList` | `docs/api/api-wen-dang2/hao-you-cao-zuo/getImAddressList.md` |
| `hao_you_cao_zuo_getOpenImContact` | 获取企微联系人信息 | `POST` | `/getOpenImContact` | `docs/api/api-wen-dang2/hao-you-cao-zuo/getOpenImContact.md` |
| `hao_you_cao_zuo_huo_qu_zi_ji_de_er_wei_ma` | 获取我的二维码 | `POST` | `/getQrCode` | `docs/api/api-wen-dang2/hao-you-cao-zuo/huo-qu-zi-ji-de-er-wei-ma.md` |
| `hao_you_cao_zuo_queryUserInfo` | 获取联系人信息 | `POST` | `/getContact` | `docs/api/api-wen-dang2/hao-you-cao-zuo/queryUserInfo.md` |
| `hao_you_cao_zuo_serchUser` | 搜索联系人 | `POST` | `/searchUser` | `docs/api/api-wen-dang2/hao-you-cao-zuo/serchUser.md` |
| `hao_you_cao_zuo_setDisturb` | 设置聊天免打扰 | `POST` | `/setDisturb` | `docs/api/api-wen-dang2/hao-you-cao-zuo/setDisturb.md` |
| `hao_you_cao_zuo_setFriendPermission` | 设置好友权限 | `POST` | `/setFriendPemission` | `docs/api/api-wen-dang2/hao-you-cao-zuo/setFriendPermission.md` |
| `hao_you_cao_zuo_setTop` | 设置聊天置顶 | `POST` | `/setTop` | `docs/api/api-wen-dang2/hao-you-cao-zuo/setTop.md` |
| `hao_you_cao_zuo_shan_chu_hao_you` | 删除好友 | `POST` | `/delContact` | `docs/api/api-wen-dang2/hao-you-cao-zuo/shan-chu-hao-you.md` |
| `hao_you_cao_zuo_she_zhi_ge_ren_tou_tou_xiang` | 设置个人头头像 | `POST` | `/sendHeadImage` | `docs/api/api-wen-dang2/hao-you-cao-zuo/she-zhi-ge-ren-tou-tou-xiang.md` |
| `hao_you_cao_zuo_userPrivacySettings` | 添加隐私设置 | `POST` | `/userPrivacySettings` | `docs/api/api-wen-dang2/hao-you-cao-zuo/userPrivacySettings.md` |
| `hao_you_cao_zuo_xiu_gai_hao_you_bei_zhu` | 修改好友备注 | `POST` | `/modifyRemark` | `docs/api/api-wen-dang2/hao-you-cao-zuo/xiu-gai-hao-you-bei-zhu.md` |

## Module: `peng-you-quan`

| operationId | title | method | path | doc |
|---|---|---|---|---|
| `peng_you_quan_asynSnsSendVideo` | 异步发送视频朋友圈 | `POST` | `/asynSnsSendVideo` | `docs/api/api-wen-dang2/peng-you-quan/asynSnsSendVideo.md` |
| `peng_you_quan_deleteSns` | 删除朋友圈 | `POST` | `/deleteSns` | `docs/api/api-wen-dang2/peng-you-quan/deleteSns.md` |
| `peng_you_quan_downloadSnsVideo` | 下载朋友圈视频 | `POST` | `/downloadSnsVideo` | `docs/api/api-wen-dang2/peng-you-quan/downloadSnsVideo.md` |
| `peng_you_quan_forwardSns` | 转发朋友圈 | `POST` | `/forwardSns` | `docs/api/api-wen-dang2/peng-you-quan/forwardSns.md` |
| `peng_you_quan_getAsynSnsSendVideoRes` | 获取发送视频朋友圈结果 | `POST` | `/getAsynSnsSendVideoRes` | `docs/api/api-wen-dang2/peng-you-quan/getAsynSnsSendVideoRes.md` |
| `peng_you_quan_getCircle` | 获取朋友圈 | `POST` | `/getCircle` | `docs/api/api-wen-dang2/peng-you-quan/getCircle.md` |
| `peng_you_quan_getFriendCircle` | 获取某个好友的朋友圈 | `POST` | `/getFriendCircle` | `docs/api/api-wen-dang2/peng-you-quan/getFriendCircle.md` |
| `peng_you_quan_getSnsObject` | 获取某条朋友圈详细内容 | `POST` | `/getSnsObject` | `docs/api/api-wen-dang2/peng-you-quan/getSnsObject.md` |
| `peng_you_quan_snsCancelPraise` | 取消点赞 | `POST` | `/snsCancelPraise` | `docs/api/api-wen-dang2/peng-you-quan/snsCancelPraise.md` |
| `peng_you_quan_snsComment` | 朋友圈评论 | `POST` | `/snsComment` | `docs/api/api-wen-dang2/peng-you-quan/snsComment.md` |
| `peng_you_quan_snsCommentDel` | 删除某条朋友圈的某条评论 | `POST` | `/snsCommentDel` | `docs/api/api-wen-dang2/peng-you-quan/snsCommentDel.md` |
| `peng_you_quan_snsPraise` | 朋友圈点赞 | `POST` | `/snsPraise` | `docs/api/api-wen-dang2/peng-you-quan/snsPraise.md` |
| `peng_you_quan_snsPrivacySettings` | 朋友圈权限设置 | `POST` | `/snsPrivacySettings` | `docs/api/api-wen-dang2/peng-you-quan/snsPrivacySettings.md` |
| `peng_you_quan_snsSend` | 发送文字朋友圈消息 | `POST` | `/snsSend` | `docs/api/api-wen-dang2/peng-you-quan/snsSend.md` |
| `peng_you_quan_snsSendImage` | 发送图片朋友圈消息 | `POST` | `/snsSendImage` | `docs/api/api-wen-dang2/peng-you-quan/snsSendImage.md` |
| `peng_you_quan_snsSendUrl` | 发送链接朋友圈消息 | `POST` | `/snsSendUrl` | `docs/api/api-wen-dang2/peng-you-quan/snsSendUrl.md` |
| `peng_you_quan_snsSetAsPrivacy` | 设置某条朋友圈为隐私 | `POST` | `/snsSetAsPrivacy` | `docs/api/api-wen-dang2/peng-you-quan/snsSetAsPrivacy.md` |
| `peng_you_quan_snsSetPublic` | 设置某条朋友圈为公开 | `POST` | `/snsSetPublic` | `docs/api/api-wen-dang2/peng-you-quan/snsSetPublic.md` |

## Module: `qun-cao-zuo`

| operationId | title | method | path | doc |
|---|---|---|---|---|
| `qun_cao_zuo_acceptMemberGroup` | 自动通过群（url） | `POST` | `/acceptUrl` | `docs/api/api-wen-dang2/qun-cao-zuo/acceptMemberGroup.md` |
| `qun_cao_zuo_addChatRoomMemberVerify` | 邀请群成员（开启群验证） | `POST` | `/addChatRoomMemberVerify` | `docs/api/api-wen-dang2/qun-cao-zuo/addChatRoomMemberVerify.md` |
| `qun_cao_zuo_addGroupMember` | 添加群成员 | `POST` | `/addChatRoomMember` | `docs/api/api-wen-dang2/qun-cao-zuo/addGroupMember.md` |
| `qun_cao_zuo_addRoomMemberFriend` | 添加群成员为好友 | `POST` | `/addRoomMemberFriend` | `docs/api/api-wen-dang2/qun-cao-zuo/addRoomMemberFriend.md` |
| `qun_cao_zuo_agreeAddChatRoomMember` | 群管理确认入群邀请 | `POST` | `/agreeAddChatRoomMember` | `docs/api/api-wen-dang2/qun-cao-zuo/agreeAddChatRoomMember.md` |
| `qun_cao_zuo_chuang_jian_wei_xin_qun` | 创建微信群 | `POST` | `/createChatroom` | `docs/api/api-wen-dang2/qun-cao-zuo/chuang-jian-wei-xin-qun.md` |
| `qun_cao_zuo_delGroupMember` | 删除群成员 | `POST` | `/deleteChatRoomMember` | `docs/api/api-wen-dang2/qun-cao-zuo/delGroupMember.md` |
| `qun_cao_zuo_inviteGroupMember` | 邀请群成员（40人以上） | `POST` | `/inviteChatRoomMember` | `docs/api/api-wen-dang2/qun-cao-zuo/inviteGroupMember.md` |
| `qun_cao_zuo_operateChatRoom` | 群管理操作 | `POST` | `/operateChatRoom` | `docs/api/api-wen-dang2/qun-cao-zuo/operateChatRoom.md` |
| `qun_cao_zuo_queryGroupDetail` | 获取群信息 | `POST` | `/getChatRoomInfo` | `docs/api/api-wen-dang2/qun-cao-zuo/queryGroupDetail.md` |
| `qun_cao_zuo_queryGroupList` | 获取群成员 | `POST` | `/getChatRoomMember` | `docs/api/api-wen-dang2/qun-cao-zuo/queryGroupList.md` |
| `qun_cao_zuo_queryGroupMemberDetail` | 获取群成员详情 | `POST` | `/getChatRoomMemberInfo` | `docs/api/api-wen-dang2/qun-cao-zuo/queryGroupMemberDetail.md` |
| `qun_cao_zuo_queryGroupQrCode` | 获取群二维码 | `POST` | `/getGroupQrCode` | `docs/api/api-wen-dang2/qun-cao-zuo/queryGroupQrCode.md` |
| `qun_cao_zuo_quitGroup` | 退出群聊 | `POST` | `/quitChatRoom` | `docs/api/api-wen-dang2/qun-cao-zuo/quitGroup.md` |
| `qun_cao_zuo_roomAppTodo` | 设置群待办消息 | `POST` | `/roomAppTodo` | `docs/api/api-wen-dang2/qun-cao-zuo/roomAppTodo.md` |
| `qun_cao_zuo_roomTodo` | 设置群待办消息 | `POST` | `/roomTodo` | `docs/api/api-wen-dang2/qun-cao-zuo/roomTodo.md` |
| `qun_cao_zuo_saveGroup` | 群保存\|取消到通讯录 | `POST` | `/showInAddressBook` | `docs/api/api-wen-dang2/qun-cao-zuo/saveGroup.md` |
| `qun_cao_zuo_scanJoinRoom` | 扫码入群 | `POST` | `/scanJoinRoom` | `docs/api/api-wen-dang2/qun-cao-zuo/scanJoinRoom.md` |
| `qun_cao_zuo_setGroupAnnounct` | 设置群公告 | `POST` | `/setChatRoomAnnouncement` | `docs/api/api-wen-dang2/qun-cao-zuo/setGroupAnnounct.md` |
| `qun_cao_zuo_updateGroupName` | 修改群名称 | `POST` | `/modifyGroupName` | `docs/api/api-wen-dang2/qun-cao-zuo/updateGroupName.md` |
| `qun_cao_zuo_updateGroupRemark` | 修改群备注 | `POST` | `/modifyGroupRemark` | `docs/api/api-wen-dang2/qun-cao-zuo/updateGroupRemark.md` |
| `qun_cao_zuo_updateIInChatRoomNickName` | 修改我在某群的昵称 | `POST` | `/updateIInChatRoomNickName` | `docs/api/api-wen-dang2/qun-cao-zuo/updateIInChatRoomNickName.md` |

## Module: `shipinhao`

| operationId | title | method | path | doc |
|---|---|---|---|---|
| `shipinhao_createFinder` | 创建视频号 | `POST` | `/createFinder` | `docs/api/api-wen-dang2/shipinhao/createFinder.md` |
| `shipinhao_finderBrowse` | 浏览 | `POST` | `/finderBrowse` | `docs/api/api-wen-dang2/shipinhao/finderBrowse.md` |
| `shipinhao_finderComment` | 评论 | `POST` | `/finderComment` | `docs/api/api-wen-dang2/shipinhao/finderComment.md` |
| `shipinhao_finderCommentDetails` | 获取评论列表 | `POST` | `/finderCommentDetails` | `docs/api/api-wen-dang2/shipinhao/finderCommentDetails.md` |
| `shipinhao_finderFollow` | 关注 | `POST` | `/finderFollow` | `docs/api/api-wen-dang2/shipinhao/finderFollow.md` |
| `shipinhao_finderHome` | 获取个人主页 | `POST` | `/finderHome` | `docs/api/api-wen-dang2/shipinhao/finderHome.md` |
| `shipinhao_finderIdFav` | 点赞 | `POST` | `/finderIdFav` | `docs/api/api-wen-dang2/shipinhao/finderIdFav.md` |
| `shipinhao_finderIdLike` | 小红心 | `POST` | `/finderIdLike` | `docs/api/api-wen-dang2/shipinhao/finderIdLike.md` |
| `shipinhao_finderPublish` | 发布视频号 | `POST` | `/finderPublish` | `docs/api/api-wen-dang2/shipinhao/finderPublish.md` |
| `shipinhao_finderUpload` | 上传视频号视频 | `POST` | `/finderUpload` | `docs/api/api-wen-dang2/shipinhao/finderUpload.md` |
| `shipinhao_finderUserHome` | 获取用户主页 | `POST` | `/finderUserHome` | `docs/api/api-wen-dang2/shipinhao/finderUserHome.md` |
| `shipinhao_getContactDetails` | 获取私信联系人信息 | `POST` | `/finder/getContactDetails` | `docs/api/api-wen-dang2/shipinhao/getContactDetails.md` |
| `shipinhao_getFollowList` | 获取关注列表 | `POST` | `/finder/getFollowList` | `docs/api/api-wen-dang2/shipinhao/getFollowList.md` |
| `shipinhao_getLikeAndFavList` | 获取赞和收藏的视频列表 | `POST` | `/finder/getLikeAndFavList` | `docs/api/api-wen-dang2/shipinhao/getLikeAndFavList.md` |
| `shipinhao_getMentionList` | 消息列表 | `POST` | `/finder/getMentionList` | `docs/api/api-wen-dang2/shipinhao/getMentionList.md` |
| `shipinhao_getQrCode` | 获取我的视频号二维码 | `POST` | `/finder/getQrCode` | `docs/api/api-wen-dang2/shipinhao/getQrCode.md` |
| `shipinhao_getSessionId` | 获取私信SessionId | `POST` | `/getSessionId` | `docs/api/api-wen-dang2/shipinhao/getSessionId.md` |
| `shipinhao_modFinderProfile` | 修改视频号资料 | `POST` | `/modFinderProfile` | `docs/api/api-wen-dang2/shipinhao/modFinderProfile.md` |
| `shipinhao_privateSend` | 私信文字 | `POST` | `/privateSend` | `docs/api/api-wen-dang2/shipinhao/privateSend.md` |
| `shipinhao_privateSendImg` | 私信图片 | `POST` | `/privateSendImg` | `docs/api/api-wen-dang2/shipinhao/privateSendImg.md` |
| `shipinhao_scanFinderHelper` | 登录视频号助手 | `POST` | `/scanFinderHelper` | `docs/api/api-wen-dang2/shipinhao/scanFinderHelper.md` |
| `shipinhao_searchFinder` | 搜索视频号 | `POST` | `/newSearchFinder` | `docs/api/api-wen-dang2/shipinhao/searchFinder.md` |

## Module: `shou-cang-jia`

| operationId | title | method | path | doc |
|---|---|---|---|---|
| `shou_cang_jia_huo_qu_shou_cang_jia_lie_biao` | 获取收藏夹列表 | `POST` | `/weChatFavorites/favSync` | `docs/api/api-wen-dang2/shou-cang-jia/huo-qu-shou-cang-jia-lie-biao.md` |
| `shou_cang_jia_huo_qu_shou_cang_jia_nei_rong` | 获取收藏夹内容 | `POST` | `/weChatFavorites/getFavItem` | `docs/api/api-wen-dang2/shou-cang-jia/huo-qu-shou-cang-jia-nei-rong.md` |
| `shou_cang_jia_shan_chu_shou_cang_jia_nei_rong` | 删除收藏夹内容 | `POST` | `/weChatFavorites/delFavItem` | `docs/api/api-wen-dang2/shou-cang-jia/shan-chu-shou-cang-jia-nei-rong.md` |

## Module: `te-shu`

| operationId | title | method | path | doc |
|---|---|---|---|---|
| `te_shu_cdnDownFile` | CDN资源下载 | `POST` | `/cdnDownFile` | `docs/api/api-wen-dang2/te-shu/cdnDownFile.md` |
| `te_shu_getReqTimes` | 查询接口调用次数 | `POST` | `/getReqTimes` | `docs/api/api-wen-dang2/te-shu/getReqTimes.md` |
| `te_shu_getUserFlow` | 查询使用流量 | `POST` | `/getUserFlow` | `docs/api/api-wen-dang2/te-shu/getUserFlow.md` |
| `te_shu_offlineReason` | 查询掉线原因 | `POST` | `/offlineReason` | `docs/api/api-wen-dang2/te-shu/offlineReason.md` |
| `te_shu_sendCdnVideo` | CDN视频上传 | `POST` | `/sendCdnVideo` | `docs/api/api-wen-dang2/te-shu/sendCdnVideo.md` |
| `te_shu_setproxy` | 动态设置代理IP | `POST` | `/setproxy` | `docs/api/api-wen-dang2/te-shu/setproxy.md` |
| `te_shu_uploadCdnImage` | CDN图片上传 | `POST` | `/uploadCdnImage` | `docs/api/api-wen-dang2/te-shu/uploadCdnImage.md` |

## Module: `wei-xin-guan-li`

| operationId | title | method | path | doc |
|---|---|---|---|---|
| `wei_xin_guan_li_cha_xun_wei_xin_shi_fou_zai_xian` | 查询微信是否在线 | `POST` | `/isOnline` | `docs/api/api-wen-dang2/wei-xin-guan-li/cha-xun-wei-xin-shi-fou-zai-xian.md` |
| `wei_xin_guan_li_duan_xian_chong_lian` | 查询账号中在线的微信列表 | `POST` | `/queryLoginWx` | `docs/api/api-wen-dang2/wei-xin-guan-li/duan-xian-chong-lian.md` |
| `wei_xin_guan_li_pi_liang_xia_xian_wei_xin_hao` | 批量下线微信号 | `POST` | `/member/offline` | `docs/api/api-wen-dang2/wei-xin-guan-li/pi-liang-xia-xian-wei-xin-hao.md` |

## Module: `xiao-xi-fa-song`

| operationId | title | method | path | doc |
|---|---|---|---|---|
| `xiao_xi_fa_song_fa_song_emoji` | 发送emoji表情 | `POST` | `/sendEmoji` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-emoji.md` |
| `xiao_xi_fa_song_fa_song_lian_jie_xiao_xi` | 发送链接 | `POST` | `/sendUrl` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-lian-jie-xiao-xi.md` |
| `xiao_xi_fa_song_fa_song_ming_pian_xiao_xi` | 发送名片消息 | `POST` | `/sendNameCard` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-ming-pian-xiao-xi.md` |
| `xiao_xi_fa_song_fa_song_shi_pin_xiao_xi` | 发送视频消息 | `POST` | `/sendVideo` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-shi-pin-xiao-xi.md` |
| `xiao_xi_fa_song_fa_song_tu_pian_xiao_xi2` | 发送图片消息 | `POST` | `/sendImage2` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-tu-pian-xiao-xi2.md` |
| `xiao_xi_fa_song_fa_song_wen_ben_xiao_xi` | 发送文本消息 | `POST` | `/sendText` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-wen-ben-xiao-xi.md` |
| `xiao_xi_fa_song_fa_song_yi_jing_shou_dao_de_shi_pin_xiao_xi` | 转发视频消息 | `POST` | `/sendRecvVideo` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-yi-jing-shou-dao-de-shi-pin-xiao-xi.md` |
| `xiao_xi_fa_song_fa_song_yi_jing_shou_dao_de_tu_pian_xiao_xi` | 转发图片消息 | `POST` | `/sendRecvImage` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-yi-jing-shou-dao-de-tu-pian-xiao-xi.md` |
| `xiao_xi_fa_song_fa_song_yi_jing_shou_dao_de_wen_jian` | 转发文件消息 | `POST` | `/sendRecvFile` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-yi-jing-shou-dao-de-wen-jian.md` |
| `xiao_xi_fa_song_fa_song_yu_yin_xiao_xi_ji_jiang_kai_fang` | 发送语音 | `POST` | `/sendVoice` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-yu-yin-xiao-xi-ji-jiang-kai-fang.md` |
| `xiao_xi_fa_song_forwardUrl` | 转发链接消息 | `POST` | `/forwardUrl` | `docs/api/api-wen-dang2/xiao-xi-fa-song/forwardUrl.md` |
| `xiao_xi_fa_song_qun_liao_at` | 群聊@ | `POST` | `/sendText` | `docs/api/api-wen-dang2/xiao-xi-fa-song/qun-liao-at.md` |
| `xiao_xi_fa_song_revokeMsg` | 撤回消息 | `POST` | `/revokeMsg` | `docs/api/api-wen-dang2/xiao-xi-fa-song/revokeMsg.md` |
| `xiao_xi_fa_song_sendApp` | 发送APP类消息 | `POST` | `/sendApplet` | `docs/api/api-wen-dang2/xiao-xi-fa-song/sendApp.md` |
| `xiao_xi_fa_song_sendApplet` | 转发小程序 | `POST` | `/sendApplet` | `docs/api/api-wen-dang2/xiao-xi-fa-song/sendApplet.md` |
| `xiao_xi_fa_song_sendApplets` | 发送小程序 | `POST` | `/sendApplets` | `docs/api/api-wen-dang2/xiao-xi-fa-song/sendApplets.md` |
| `xiao_xi_fa_song_sendFile` | 发送文件 | `POST` | `/sendFile` | `docs/api/api-wen-dang2/xiao-xi-fa-song/sendFile.md` |
| `xiao_xi_fa_song_sendFileBase64` | 发送文件 | `POST` | `/sendFileBase64` | `docs/api/api-wen-dang2/xiao-xi-fa-song/sendFileBase64.md` |

## Module: `xiao-xi-jie-shou`

| operationId | title | method | path | doc |
|---|---|---|---|---|
| `xiao_xi_jie_shou_asynGetMsgVideo` | 异步下载消息中的视频 | `POST` | `/asynGetMsgVideo` | `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/asynGetMsgVideo.md` |
| `xiao_xi_jie_shou_getMsgEmoji` | 下载消息中的动图 | `POST` | `/getMsgEmoji` | `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/getMsgEmoji.md` |
| `xiao_xi_jie_shou_getMsgVideoRes` | 获取异步下载视频消息结果 | `POST` | `/getMsgVideoRes` | `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/getMsgVideoRes.md` |
| `xiao_xi_jie_shou_qu_xiao_xiao_xi_jie_shou` | 取消消息接收 | `POST` | `/cancelHttpCallbackUrl` | `docs/api/api-wen-dang2/xiao-xi-jie-shou/shou-xiao-xi/qu-xiao-xiao-xi-jie-shou.md` |
| `xiao_xi_jie_shou_she_zhi_http_hui_tiao_di_zhi` | 设置消息接收地址 | `POST` | `/setHttpCallbackUrl` | `docs/api/api-wen-dang2/xiao-xi-jie-shou/shou-xiao-xi/she-zhi-http-hui-tiao-di-zhi.md` |
| `xiao_xi_jie_shou_xia_zai_tu_pian_ji_jiang_kai_fang` | 下载图片 | `POST` | `/getMsgImg` | `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/xia-zai-tu-pian-ji-jiang-kai-fang.md` |
| `xiao_xi_jie_shou_xia_zai_wen_jian_ji_jiang_kai_fang` | 下载文件 | `POST` | `/getMsgFile` | `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/xia-zai-wen-jian-ji-jiang-kai-fang.md` |
| `xiao_xi_jie_shou_xia_zai_yu_yin_ji_jiang_kai_fang` | 下载消息中的语音 | `POST` | `/getMsgVoice` | `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/xia-zai-yu-yin-ji-jiang-kai-fang.md` |
