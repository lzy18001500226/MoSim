# API Spec（从离线文档生成）

Generated at: `2026-02-10T11:37:09.305Z`

本文件由离线文档自动提取生成，用于 SDK 工程落地：
- 提供 **全量 endpoint 清单**（method/path/参数/返回/鉴权）
- 作为实现与测试的“需求输入”（避免遗漏接口）

权威来源仍为 `docs/api/` 中的接口说明文档；当解析与原文不一致时，以原文为准，并更新解析规则与本文件。

Catalog JSON: `docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json`

## 全局约定（提炼自离线文档）

- `baseUrl`：文档中使用 `http://域名地址/...` 占位，SDK 必须允许使用方配置。
- `Authorization`：多数接口需要该请求头（来自登录接口返回）。SDK 默认 **原文注入**，是否添加前缀由配置控制。
- 响应：常见为 `{ code, message/msg, data }`；其中 `code == 1000` 表示成功，`1001` 表示失败（接口间可能存在差异，SDK 需允许接口级覆盖）。

## 目录

| module | operationId | title | method | path | doc |
|---|---|---|---|---|---|
| `biao-qian` | `biao_qian_addContactLabel` | 创建标签 | `POST` | `/addContactLabel` | `docs/api/api-wen-dang2/biao-qian/addContactLabel.md` |
| `biao-qian` | `biao_qian_delContactLabel` | 删除联系人标签 | `POST` | `/delContactLabel` | `docs/api/api-wen-dang2/biao-qian/delContactLabel.md` |
| `biao-qian` | `biao_qian_getContactLabelList` | 获取标签列表 | `POST` | `/getContactLabelList` | `docs/api/api-wen-dang2/biao-qian/getContactLabelList.md` |
| `biao-qian` | `biao_qian_modifyContactLabel` | 修改联系人标签 | `POST` | `/modifyContactLabel` | `docs/api/api-wen-dang2/biao-qian/modifyContactLabel.md` |
| `deng-lu` | `deng_lu_deng_lu_wei_kong_ping_tai_di_yi_bu` | 登录E云平台（第一步） | `POST` | `/member/login` | `docs/api/api-wen-dang2/deng-lu/deng-lu-wei-kong-ping-tai-di-yi-bu.md` |
| `deng-lu` | `deng_lu_er_ci_deng_lu` | 弹框登录 | `POST` | `/secondLogin` | `docs/api/api-wen-dang2/deng-lu/er-ci-deng-lu.md` |
| `deng-lu` | `deng_lu_huo_qu_wei_xin_er_wei_ma2` | 获取二维码（第二步-方式1） | `POST` | `/iPadLogin` | `docs/api/api-wen-dang2/deng-lu/huo-qu-wei-xin-er-wei-ma2.md` |
| `deng-lu` | `deng_lu_initFriendList` | 初始化通讯录列表 | `POST` | `/initAddressList` | `docs/api/api-wen-dang2/deng-lu/initFriendList.md` |
| `deng-lu` | `deng_lu_queryFriendList` | 获取通讯录列表 | `POST` | `/getAddressList` | `docs/api/api-wen-dang2/deng-lu/queryFriendList.md` |
| `deng-lu` | `deng_lu_zhang_hao_mi_ma_deng_lu` | 账号密码登录 | `POST` | `/loginByAccountAndPassword` | `docs/api/api-wen-dang2/deng-lu/zhang-hao-mi-ma-deng-lu.md` |
| `deng-lu` | `deng_lu_zhi_xing_wei_xin_deng_lu` | 执行微信登录（第三步） | `POST` | `/getIPadLoginInfo` | `docs/api/api-wen-dang2/deng-lu/zhi-xing-wei-xin-deng-lu.md` |
| `hao-you-cao-zuo` | `hao_you_cao_zuo_acceptUser` | 同意添加好友 | `POST` | `/acceptUser` | `docs/api/api-wen-dang2/hao-you-cao-zuo/acceptUser.md` |
| `hao-you-cao-zuo` | `hao_you_cao_zuo_addFriend` | 添加好友 | `POST` | `/addUser` | `docs/api/api-wen-dang2/hao-you-cao-zuo/addFriend.md` |
| `hao-you-cao-zuo` | `hao_you_cao_zuo_checkZombie` | 检测好友状态 | `POST` | `/checkZombie` | `docs/api/api-wen-dang2/hao-you-cao-zuo/checkZombie.md` |
| `hao-you-cao-zuo` | `hao_you_cao_zuo_getImAddressList` | 获取企微联系人列表 | `POST` | `/getImAddressList` | `docs/api/api-wen-dang2/hao-you-cao-zuo/getImAddressList.md` |
| `hao-you-cao-zuo` | `hao_you_cao_zuo_getOpenImContact` | 获取企微联系人信息 | `POST` | `/getOpenImContact` | `docs/api/api-wen-dang2/hao-you-cao-zuo/getOpenImContact.md` |
| `hao-you-cao-zuo` | `hao_you_cao_zuo_huo_qu_zi_ji_de_er_wei_ma` | 获取我的二维码 | `POST` | `/getQrCode` | `docs/api/api-wen-dang2/hao-you-cao-zuo/huo-qu-zi-ji-de-er-wei-ma.md` |
| `hao-you-cao-zuo` | `hao_you_cao_zuo_queryUserInfo` | 获取联系人信息 | `POST` | `/getContact` | `docs/api/api-wen-dang2/hao-you-cao-zuo/queryUserInfo.md` |
| `hao-you-cao-zuo` | `hao_you_cao_zuo_serchUser` | 搜索联系人 | `POST` | `/searchUser` | `docs/api/api-wen-dang2/hao-you-cao-zuo/serchUser.md` |
| `hao-you-cao-zuo` | `hao_you_cao_zuo_setDisturb` | 设置聊天免打扰 | `POST` | `/setDisturb` | `docs/api/api-wen-dang2/hao-you-cao-zuo/setDisturb.md` |
| `hao-you-cao-zuo` | `hao_you_cao_zuo_setFriendPermission` | 设置好友权限 | `POST` | `/setFriendPemission` | `docs/api/api-wen-dang2/hao-you-cao-zuo/setFriendPermission.md` |
| `hao-you-cao-zuo` | `hao_you_cao_zuo_setTop` | 设置聊天置顶 | `POST` | `/setTop` | `docs/api/api-wen-dang2/hao-you-cao-zuo/setTop.md` |
| `hao-you-cao-zuo` | `hao_you_cao_zuo_shan_chu_hao_you` | 删除好友 | `POST` | `/delContact` | `docs/api/api-wen-dang2/hao-you-cao-zuo/shan-chu-hao-you.md` |
| `hao-you-cao-zuo` | `hao_you_cao_zuo_she_zhi_ge_ren_tou_tou_xiang` | 设置个人头头像 | `POST` | `/sendHeadImage` | `docs/api/api-wen-dang2/hao-you-cao-zuo/she-zhi-ge-ren-tou-tou-xiang.md` |
| `hao-you-cao-zuo` | `hao_you_cao_zuo_userPrivacySettings` | 添加隐私设置 | `POST` | `/userPrivacySettings` | `docs/api/api-wen-dang2/hao-you-cao-zuo/userPrivacySettings.md` |
| `hao-you-cao-zuo` | `hao_you_cao_zuo_xiu_gai_hao_you_bei_zhu` | 修改好友备注 | `POST` | `/modifyRemark` | `docs/api/api-wen-dang2/hao-you-cao-zuo/xiu-gai-hao-you-bei-zhu.md` |
| `peng-you-quan` | `peng_you_quan_asynSnsSendVideo` | 异步发送视频朋友圈 | `POST` | `/asynSnsSendVideo` | `docs/api/api-wen-dang2/peng-you-quan/asynSnsSendVideo.md` |
| `peng-you-quan` | `peng_you_quan_deleteSns` | 删除朋友圈 | `POST` | `/deleteSns` | `docs/api/api-wen-dang2/peng-you-quan/deleteSns.md` |
| `peng-you-quan` | `peng_you_quan_downloadSnsVideo` | 下载朋友圈视频 | `POST` | `/downloadSnsVideo` | `docs/api/api-wen-dang2/peng-you-quan/downloadSnsVideo.md` |
| `peng-you-quan` | `peng_you_quan_forwardSns` | 转发朋友圈 | `POST` | `/forwardSns` | `docs/api/api-wen-dang2/peng-you-quan/forwardSns.md` |
| `peng-you-quan` | `peng_you_quan_getAsynSnsSendVideoRes` | 获取发送视频朋友圈结果 | `POST` | `/getAsynSnsSendVideoRes` | `docs/api/api-wen-dang2/peng-you-quan/getAsynSnsSendVideoRes.md` |
| `peng-you-quan` | `peng_you_quan_getCircle` | 获取朋友圈 | `POST` | `/getCircle` | `docs/api/api-wen-dang2/peng-you-quan/getCircle.md` |
| `peng-you-quan` | `peng_you_quan_getFriendCircle` | 获取某个好友的朋友圈 | `POST` | `/getFriendCircle` | `docs/api/api-wen-dang2/peng-you-quan/getFriendCircle.md` |
| `peng-you-quan` | `peng_you_quan_getSnsObject` | 获取某条朋友圈详细内容 | `POST` | `/getSnsObject` | `docs/api/api-wen-dang2/peng-you-quan/getSnsObject.md` |
| `peng-you-quan` | `peng_you_quan_snsCancelPraise` | 取消点赞 | `POST` | `/snsCancelPraise` | `docs/api/api-wen-dang2/peng-you-quan/snsCancelPraise.md` |
| `peng-you-quan` | `peng_you_quan_snsComment` | 朋友圈评论 | `POST` | `/snsComment` | `docs/api/api-wen-dang2/peng-you-quan/snsComment.md` |
| `peng-you-quan` | `peng_you_quan_snsCommentDel` | 删除某条朋友圈的某条评论 | `POST` | `/snsCommentDel` | `docs/api/api-wen-dang2/peng-you-quan/snsCommentDel.md` |
| `peng-you-quan` | `peng_you_quan_snsPraise` | 朋友圈点赞 | `POST` | `/snsPraise` | `docs/api/api-wen-dang2/peng-you-quan/snsPraise.md` |
| `peng-you-quan` | `peng_you_quan_snsPrivacySettings` | 朋友圈权限设置 | `POST` | `/snsPrivacySettings` | `docs/api/api-wen-dang2/peng-you-quan/snsPrivacySettings.md` |
| `peng-you-quan` | `peng_you_quan_snsSend` | 发送文字朋友圈消息 | `POST` | `/snsSend` | `docs/api/api-wen-dang2/peng-you-quan/snsSend.md` |
| `peng-you-quan` | `peng_you_quan_snsSendImage` | 发送图片朋友圈消息 | `POST` | `/snsSendImage` | `docs/api/api-wen-dang2/peng-you-quan/snsSendImage.md` |
| `peng-you-quan` | `peng_you_quan_snsSendUrl` | 发送链接朋友圈消息 | `POST` | `/snsSendUrl` | `docs/api/api-wen-dang2/peng-you-quan/snsSendUrl.md` |
| `peng-you-quan` | `peng_you_quan_snsSetAsPrivacy` | 设置某条朋友圈为隐私 | `POST` | `/snsSetAsPrivacy` | `docs/api/api-wen-dang2/peng-you-quan/snsSetAsPrivacy.md` |
| `peng-you-quan` | `peng_you_quan_snsSetPublic` | 设置某条朋友圈为公开 | `POST` | `/snsSetPublic` | `docs/api/api-wen-dang2/peng-you-quan/snsSetPublic.md` |
| `qun-cao-zuo` | `qun_cao_zuo_acceptMemberGroup` | 自动通过群（url） | `POST` | `/acceptUrl` | `docs/api/api-wen-dang2/qun-cao-zuo/acceptMemberGroup.md` |
| `qun-cao-zuo` | `qun_cao_zuo_addChatRoomMemberVerify` | 邀请群成员（开启群验证） | `POST` | `/addChatRoomMemberVerify` | `docs/api/api-wen-dang2/qun-cao-zuo/addChatRoomMemberVerify.md` |
| `qun-cao-zuo` | `qun_cao_zuo_addGroupMember` | 添加群成员 | `POST` | `/addChatRoomMember` | `docs/api/api-wen-dang2/qun-cao-zuo/addGroupMember.md` |
| `qun-cao-zuo` | `qun_cao_zuo_addRoomMemberFriend` | 添加群成员为好友 | `POST` | `/addRoomMemberFriend` | `docs/api/api-wen-dang2/qun-cao-zuo/addRoomMemberFriend.md` |
| `qun-cao-zuo` | `qun_cao_zuo_agreeAddChatRoomMember` | 群管理确认入群邀请 | `POST` | `/agreeAddChatRoomMember` | `docs/api/api-wen-dang2/qun-cao-zuo/agreeAddChatRoomMember.md` |
| `qun-cao-zuo` | `qun_cao_zuo_chuang_jian_wei_xin_qun` | 创建微信群 | `POST` | `/createChatroom` | `docs/api/api-wen-dang2/qun-cao-zuo/chuang-jian-wei-xin-qun.md` |
| `qun-cao-zuo` | `qun_cao_zuo_delGroupMember` | 删除群成员 | `POST` | `/deleteChatRoomMember` | `docs/api/api-wen-dang2/qun-cao-zuo/delGroupMember.md` |
| `qun-cao-zuo` | `qun_cao_zuo_inviteGroupMember` | 邀请群成员（40人以上） | `POST` | `/inviteChatRoomMember` | `docs/api/api-wen-dang2/qun-cao-zuo/inviteGroupMember.md` |
| `qun-cao-zuo` | `qun_cao_zuo_operateChatRoom` | 群管理操作 | `POST` | `/operateChatRoom` | `docs/api/api-wen-dang2/qun-cao-zuo/operateChatRoom.md` |
| `qun-cao-zuo` | `qun_cao_zuo_queryGroupDetail` | 获取群信息 | `POST` | `/getChatRoomInfo` | `docs/api/api-wen-dang2/qun-cao-zuo/queryGroupDetail.md` |
| `qun-cao-zuo` | `qun_cao_zuo_queryGroupList` | 获取群成员 | `POST` | `/getChatRoomMember` | `docs/api/api-wen-dang2/qun-cao-zuo/queryGroupList.md` |
| `qun-cao-zuo` | `qun_cao_zuo_queryGroupMemberDetail` | 获取群成员详情 | `POST` | `/getChatRoomMemberInfo` | `docs/api/api-wen-dang2/qun-cao-zuo/queryGroupMemberDetail.md` |
| `qun-cao-zuo` | `qun_cao_zuo_queryGroupQrCode` | 获取群二维码 | `POST` | `/getGroupQrCode` | `docs/api/api-wen-dang2/qun-cao-zuo/queryGroupQrCode.md` |
| `qun-cao-zuo` | `qun_cao_zuo_quitGroup` | 退出群聊 | `POST` | `/quitChatRoom` | `docs/api/api-wen-dang2/qun-cao-zuo/quitGroup.md` |
| `qun-cao-zuo` | `qun_cao_zuo_roomAppTodo` | 设置群待办消息 | `POST` | `/roomAppTodo` | `docs/api/api-wen-dang2/qun-cao-zuo/roomAppTodo.md` |
| `qun-cao-zuo` | `qun_cao_zuo_roomTodo` | 设置群待办消息 | `POST` | `/roomTodo` | `docs/api/api-wen-dang2/qun-cao-zuo/roomTodo.md` |
| `qun-cao-zuo` | `qun_cao_zuo_saveGroup` | 群保存\|取消到通讯录 | `POST` | `/showInAddressBook` | `docs/api/api-wen-dang2/qun-cao-zuo/saveGroup.md` |
| `qun-cao-zuo` | `qun_cao_zuo_scanJoinRoom` | 扫码入群 | `POST` | `/scanJoinRoom` | `docs/api/api-wen-dang2/qun-cao-zuo/scanJoinRoom.md` |
| `qun-cao-zuo` | `qun_cao_zuo_setGroupAnnounct` | 设置群公告 | `POST` | `/setChatRoomAnnouncement` | `docs/api/api-wen-dang2/qun-cao-zuo/setGroupAnnounct.md` |
| `qun-cao-zuo` | `qun_cao_zuo_updateGroupName` | 修改群名称 | `POST` | `/modifyGroupName` | `docs/api/api-wen-dang2/qun-cao-zuo/updateGroupName.md` |
| `qun-cao-zuo` | `qun_cao_zuo_updateGroupRemark` | 修改群备注 | `POST` | `/modifyGroupRemark` | `docs/api/api-wen-dang2/qun-cao-zuo/updateGroupRemark.md` |
| `qun-cao-zuo` | `qun_cao_zuo_updateIInChatRoomNickName` | 修改我在某群的昵称 | `POST` | `/updateIInChatRoomNickName` | `docs/api/api-wen-dang2/qun-cao-zuo/updateIInChatRoomNickName.md` |
| `shipinhao` | `shipinhao_createFinder` | 创建视频号 | `POST` | `/createFinder` | `docs/api/api-wen-dang2/shipinhao/createFinder.md` |
| `shipinhao` | `shipinhao_finderBrowse` | 浏览 | `POST` | `/finderBrowse` | `docs/api/api-wen-dang2/shipinhao/finderBrowse.md` |
| `shipinhao` | `shipinhao_finderComment` | 评论 | `POST` | `/finderComment` | `docs/api/api-wen-dang2/shipinhao/finderComment.md` |
| `shipinhao` | `shipinhao_finderCommentDetails` | 获取评论列表 | `POST` | `/finderCommentDetails` | `docs/api/api-wen-dang2/shipinhao/finderCommentDetails.md` |
| `shipinhao` | `shipinhao_finderFollow` | 关注 | `POST` | `/finderFollow` | `docs/api/api-wen-dang2/shipinhao/finderFollow.md` |
| `shipinhao` | `shipinhao_finderHome` | 获取个人主页 | `POST` | `/finderHome` | `docs/api/api-wen-dang2/shipinhao/finderHome.md` |
| `shipinhao` | `shipinhao_finderIdFav` | 点赞 | `POST` | `/finderIdFav` | `docs/api/api-wen-dang2/shipinhao/finderIdFav.md` |
| `shipinhao` | `shipinhao_finderIdLike` | 小红心 | `POST` | `/finderIdLike` | `docs/api/api-wen-dang2/shipinhao/finderIdLike.md` |
| `shipinhao` | `shipinhao_finderPublish` | 发布视频号 | `POST` | `/finderPublish` | `docs/api/api-wen-dang2/shipinhao/finderPublish.md` |
| `shipinhao` | `shipinhao_finderUpload` | 上传视频号视频 | `POST` | `/finderUpload` | `docs/api/api-wen-dang2/shipinhao/finderUpload.md` |
| `shipinhao` | `shipinhao_finderUserHome` | 获取用户主页 | `POST` | `/finderUserHome` | `docs/api/api-wen-dang2/shipinhao/finderUserHome.md` |
| `shipinhao` | `shipinhao_getContactDetails` | 获取私信联系人信息 | `POST` | `/finder/getContactDetails` | `docs/api/api-wen-dang2/shipinhao/getContactDetails.md` |
| `shipinhao` | `shipinhao_getFollowList` | 获取关注列表 | `POST` | `/finder/getFollowList` | `docs/api/api-wen-dang2/shipinhao/getFollowList.md` |
| `shipinhao` | `shipinhao_getLikeAndFavList` | 获取赞和收藏的视频列表 | `POST` | `/finder/getLikeAndFavList` | `docs/api/api-wen-dang2/shipinhao/getLikeAndFavList.md` |
| `shipinhao` | `shipinhao_getMentionList` | 消息列表 | `POST` | `/finder/getMentionList` | `docs/api/api-wen-dang2/shipinhao/getMentionList.md` |
| `shipinhao` | `shipinhao_getQrCode` | 获取我的视频号二维码 | `POST` | `/finder/getQrCode` | `docs/api/api-wen-dang2/shipinhao/getQrCode.md` |
| `shipinhao` | `shipinhao_getSessionId` | 获取私信SessionId | `POST` | `/getSessionId` | `docs/api/api-wen-dang2/shipinhao/getSessionId.md` |
| `shipinhao` | `shipinhao_modFinderProfile` | 修改视频号资料 | `POST` | `/modFinderProfile` | `docs/api/api-wen-dang2/shipinhao/modFinderProfile.md` |
| `shipinhao` | `shipinhao_privateSend` | 私信文字 | `POST` | `/privateSend` | `docs/api/api-wen-dang2/shipinhao/privateSend.md` |
| `shipinhao` | `shipinhao_privateSendImg` | 私信图片 | `POST` | `/privateSendImg` | `docs/api/api-wen-dang2/shipinhao/privateSendImg.md` |
| `shipinhao` | `shipinhao_scanFinderHelper` | 登录视频号助手 | `POST` | `/scanFinderHelper` | `docs/api/api-wen-dang2/shipinhao/scanFinderHelper.md` |
| `shipinhao` | `shipinhao_searchFinder` | 搜索视频号 | `POST` | `/newSearchFinder` | `docs/api/api-wen-dang2/shipinhao/searchFinder.md` |
| `shou-cang-jia` | `shou_cang_jia_huo_qu_shou_cang_jia_lie_biao` | 获取收藏夹列表 | `POST` | `/weChatFavorites/favSync` | `docs/api/api-wen-dang2/shou-cang-jia/huo-qu-shou-cang-jia-lie-biao.md` |
| `shou-cang-jia` | `shou_cang_jia_huo_qu_shou_cang_jia_nei_rong` | 获取收藏夹内容 | `POST` | `/weChatFavorites/getFavItem` | `docs/api/api-wen-dang2/shou-cang-jia/huo-qu-shou-cang-jia-nei-rong.md` |
| `shou-cang-jia` | `shou_cang_jia_shan_chu_shou_cang_jia_nei_rong` | 删除收藏夹内容 | `POST` | `/weChatFavorites/delFavItem` | `docs/api/api-wen-dang2/shou-cang-jia/shan-chu-shou-cang-jia-nei-rong.md` |
| `te-shu` | `te_shu_cdnDownFile` | CDN资源下载 | `POST` | `/cdnDownFile` | `docs/api/api-wen-dang2/te-shu/cdnDownFile.md` |
| `te-shu` | `te_shu_getReqTimes` | 查询接口调用次数 | `POST` | `/getReqTimes` | `docs/api/api-wen-dang2/te-shu/getReqTimes.md` |
| `te-shu` | `te_shu_getUserFlow` | 查询使用流量 | `POST` | `/getUserFlow` | `docs/api/api-wen-dang2/te-shu/getUserFlow.md` |
| `te-shu` | `te_shu_offlineReason` | 查询掉线原因 | `POST` | `/offlineReason` | `docs/api/api-wen-dang2/te-shu/offlineReason.md` |
| `te-shu` | `te_shu_sendCdnVideo` | CDN视频上传 | `POST` | `/sendCdnVideo` | `docs/api/api-wen-dang2/te-shu/sendCdnVideo.md` |
| `te-shu` | `te_shu_setproxy` | 动态设置代理IP | `POST` | `/setproxy` | `docs/api/api-wen-dang2/te-shu/setproxy.md` |
| `te-shu` | `te_shu_uploadCdnImage` | CDN图片上传 | `POST` | `/uploadCdnImage` | `docs/api/api-wen-dang2/te-shu/uploadCdnImage.md` |
| `wei-xin-guan-li` | `wei_xin_guan_li_cha_xun_wei_xin_shi_fou_zai_xian` | 查询微信是否在线 | `POST` | `/isOnline` | `docs/api/api-wen-dang2/wei-xin-guan-li/cha-xun-wei-xin-shi-fou-zai-xian.md` |
| `wei-xin-guan-li` | `wei_xin_guan_li_duan_xian_chong_lian` | 查询账号中在线的微信列表 | `POST` | `/queryLoginWx` | `docs/api/api-wen-dang2/wei-xin-guan-li/duan-xian-chong-lian.md` |
| `wei-xin-guan-li` | `wei_xin_guan_li_pi_liang_xia_xian_wei_xin_hao` | 批量下线微信号 | `POST` | `/member/offline` | `docs/api/api-wen-dang2/wei-xin-guan-li/pi-liang-xia-xian-wei-xin-hao.md` |
| `xiao-xi-fa-song` | `xiao_xi_fa_song_fa_song_emoji` | 发送emoji表情 | `POST` | `/sendEmoji` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-emoji.md` |
| `xiao-xi-fa-song` | `xiao_xi_fa_song_fa_song_lian_jie_xiao_xi` | 发送链接 | `POST` | `/sendUrl` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-lian-jie-xiao-xi.md` |
| `xiao-xi-fa-song` | `xiao_xi_fa_song_fa_song_ming_pian_xiao_xi` | 发送名片消息 | `POST` | `/sendNameCard` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-ming-pian-xiao-xi.md` |
| `xiao-xi-fa-song` | `xiao_xi_fa_song_fa_song_shi_pin_xiao_xi` | 发送视频消息 | `POST` | `/sendVideo` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-shi-pin-xiao-xi.md` |
| `xiao-xi-fa-song` | `xiao_xi_fa_song_fa_song_tu_pian_xiao_xi2` | 发送图片消息 | `POST` | `/sendImage2` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-tu-pian-xiao-xi2.md` |
| `xiao-xi-fa-song` | `xiao_xi_fa_song_fa_song_wen_ben_xiao_xi` | 发送文本消息 | `POST` | `/sendText` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-wen-ben-xiao-xi.md` |
| `xiao-xi-fa-song` | `xiao_xi_fa_song_fa_song_yi_jing_shou_dao_de_shi_pin_xiao_xi` | 转发视频消息 | `POST` | `/sendRecvVideo` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-yi-jing-shou-dao-de-shi-pin-xiao-xi.md` |
| `xiao-xi-fa-song` | `xiao_xi_fa_song_fa_song_yi_jing_shou_dao_de_tu_pian_xiao_xi` | 转发图片消息 | `POST` | `/sendRecvImage` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-yi-jing-shou-dao-de-tu-pian-xiao-xi.md` |
| `xiao-xi-fa-song` | `xiao_xi_fa_song_fa_song_yi_jing_shou_dao_de_wen_jian` | 转发文件消息 | `POST` | `/sendRecvFile` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-yi-jing-shou-dao-de-wen-jian.md` |
| `xiao-xi-fa-song` | `xiao_xi_fa_song_fa_song_yu_yin_xiao_xi_ji_jiang_kai_fang` | 发送语音 | `POST` | `/sendVoice` | `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-yu-yin-xiao-xi-ji-jiang-kai-fang.md` |
| `xiao-xi-fa-song` | `xiao_xi_fa_song_forwardUrl` | 转发链接消息 | `POST` | `/forwardUrl` | `docs/api/api-wen-dang2/xiao-xi-fa-song/forwardUrl.md` |
| `xiao-xi-fa-song` | `xiao_xi_fa_song_qun_liao_at` | 群聊@ | `POST` | `/sendText` | `docs/api/api-wen-dang2/xiao-xi-fa-song/qun-liao-at.md` |
| `xiao-xi-fa-song` | `xiao_xi_fa_song_revokeMsg` | 撤回消息 | `POST` | `/revokeMsg` | `docs/api/api-wen-dang2/xiao-xi-fa-song/revokeMsg.md` |
| `xiao-xi-fa-song` | `xiao_xi_fa_song_sendApp` | 发送APP类消息 | `POST` | `/sendApplet` | `docs/api/api-wen-dang2/xiao-xi-fa-song/sendApp.md` |
| `xiao-xi-fa-song` | `xiao_xi_fa_song_sendApplet` | 转发小程序 | `POST` | `/sendApplet` | `docs/api/api-wen-dang2/xiao-xi-fa-song/sendApplet.md` |
| `xiao-xi-fa-song` | `xiao_xi_fa_song_sendApplets` | 发送小程序 | `POST` | `/sendApplets` | `docs/api/api-wen-dang2/xiao-xi-fa-song/sendApplets.md` |
| `xiao-xi-fa-song` | `xiao_xi_fa_song_sendFile` | 发送文件 | `POST` | `/sendFile` | `docs/api/api-wen-dang2/xiao-xi-fa-song/sendFile.md` |
| `xiao-xi-fa-song` | `xiao_xi_fa_song_sendFileBase64` | 发送文件 | `POST` | `/sendFileBase64` | `docs/api/api-wen-dang2/xiao-xi-fa-song/sendFileBase64.md` |
| `xiao-xi-jie-shou` | `xiao_xi_jie_shou_asynGetMsgVideo` | 异步下载消息中的视频 | `POST` | `/asynGetMsgVideo` | `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/asynGetMsgVideo.md` |
| `xiao-xi-jie-shou` | `xiao_xi_jie_shou_getMsgEmoji` | 下载消息中的动图 | `POST` | `/getMsgEmoji` | `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/getMsgEmoji.md` |
| `xiao-xi-jie-shou` | `xiao_xi_jie_shou_getMsgVideoRes` | 获取异步下载视频消息结果 | `POST` | `/getMsgVideoRes` | `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/getMsgVideoRes.md` |
| `xiao-xi-jie-shou` | `xiao_xi_jie_shou_qu_xiao_xiao_xi_jie_shou` | 取消消息接收 | `POST` | `/cancelHttpCallbackUrl` | `docs/api/api-wen-dang2/xiao-xi-jie-shou/shou-xiao-xi/qu-xiao-xiao-xi-jie-shou.md` |
| `xiao-xi-jie-shou` | `xiao_xi_jie_shou_she_zhi_http_hui_tiao_di_zhi` | 设置消息接收地址 | `POST` | `/setHttpCallbackUrl` | `docs/api/api-wen-dang2/xiao-xi-jie-shou/shou-xiao-xi/she-zhi-http-hui-tiao-di-zhi.md` |
| `xiao-xi-jie-shou` | `xiao_xi_jie_shou_xia_zai_tu_pian_ji_jiang_kai_fang` | 下载图片 | `POST` | `/getMsgImg` | `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/xia-zai-tu-pian-ji-jiang-kai-fang.md` |
| `xiao-xi-jie-shou` | `xiao_xi_jie_shou_xia_zai_wen_jian_ji_jiang_kai_fang` | 下载文件 | `POST` | `/getMsgFile` | `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/xia-zai-wen-jian-ji-jiang-kai-fang.md` |
| `xiao-xi-jie-shou` | `xiao_xi_jie_shou_xia_zai_yu_yin_ji_jiang_kai_fang` | 下载消息中的语音 | `POST` | `/getMsgVoice` | `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/xia-zai-yu-yin-ji-jiang-kai-fang.md` |

## 模块：`biao-qian`

### POST /addContactLabel

- operationId: `biao_qian_addContactLabel`
- title: 创建标签
- doc: `docs/api/api-wen-dang2/biao-qian/addContactLabel.md`
- requestUrl (as documented): `http://域名地址/addContactLabel`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| labelName | 是 | String | 标签名称 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /delContactLabel

- operationId: `biao_qian_delContactLabel`
- title: 删除联系人标签
- doc: `docs/api/api-wen-dang2/biao-qian/delContactLabel.md`
- requestUrl (as documented): `http://域名地址/delContactLabel`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| labelIdList | 是 | String | 标签标识，多个标签已 "，" 号分割 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /getContactLabelList

- operationId: `biao_qian_getContactLabelList`
- title: 获取标签列表
- doc: `docs/api/api-wen-dang2/biao-qian/getContactLabelList.md`
- requestUrl (as documented): `http://域名地址/getContactLabelList`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /modifyContactLabel

- operationId: `biao_qian_modifyContactLabel`
- title: 修改联系人标签
- doc: `docs/api/api-wen-dang2/biao-qian/modifyContactLabel.md`
- requestUrl (as documented): `http://域名地址/modifyContactLabel`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| wcId | 是 | String | 好友微信id |
| labelIdList | 是 | String | 标签标识，多个标签已 "，" 号分割 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

## 模块：`deng-lu`

### POST /getAddressList

- operationId: `deng_lu_queryFriendList`
- title: 获取通讯录列表
- doc: `docs/api/api-wen-dang2/deng-lu/queryFriendList.md`
- requestUrl (as documented): `http://域名地址/getAddressList`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /getIPadLoginInfo

- operationId: `deng_lu_zhi_xing_wei_xin_deng_lu`
- title: 执行微信登录（第三步）
- doc: `docs/api/api-wen-dang2/deng-lu/zhi-xing-wei-xin-deng-lu.md`
- requestUrl (as documented): `http://域名地址/getIPadLoginInfo`

**Headers（文档提取）**
- Content-Type: application/json
- **Authorization: login接口返回**

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | **登录实例标识** |
| autoCheck | 是 | boolean | 是否自动验证【说明:设备类型为Mac时使用，其它情况传false】 |
| verifyCode | 否 | string | 验证码 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| **wcId** | string |  |

### POST /initAddressList

- operationId: `deng_lu_initFriendList`
- title: 初始化通讯录列表
- doc: `docs/api/api-wen-dang2/deng-lu/initFriendList.md`
- requestUrl (as documented): `http://域名地址/initAddressList`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功、1001失败 |
| msg | string | 反馈信息 |
| data | JSONObject | 无 |

### POST /iPadLogin

- operationId: `deng_lu_huo_qu_wei_xin_er_wei_ma2`
- title: 获取二维码（第二步-方式1）
- doc: `docs/api/api-wen-dang2/deng-lu/huo-qu-wei-xin-er-wei-ma2.md`
- requestUrl (as documented): `http://域名地址/iPadLogin`

**Headers（文档提取）**
- Content-Type: application/json
- **Authorization: login接口返回**

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| **wcId** | 是 | string | 微信原始id （首次登录平台的号传""，掉线重登必须传值，否则会频繁掉线！！！） [第3步](zhi-xing-wei-xin-deng-lu.html)会返回此字段，记得入库保存 |
| deviceType | 是 | string | 设备类型：ipad【推荐】、mac |
| proxy | 是 | int |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| **wId** | string | 登录实例标识 **（本值非固定的，每次重新登录会返回新的，数据库记得实时更新wid）** |
| qrCodeUrl | string | 扫码登录地址 |

### POST /loginByAccountAndPassword

- operationId: `deng_lu_zhang_hao_mi_ma_deng_lu`
- title: 账号密码登录
- doc: `docs/api/api-wen-dang2/deng-lu/zhang-hao-mi-ma-deng-lu.md`
- requestUrl (as documented): `http://域名地址/loginByAccountAndPassword`

**Headers（文档提取）**
- Content-Type: application/json
- **Authorization: login接口返回**

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 否 | string | **登录实例标识** |
| **wcId** | 否 | string | 微信原始id （首次登录平台的号传""，掉线重登必须传值，否则会频繁掉线！！！） |
| proxy | 是 | int |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| **wId** | string | 登录实例标识 **（本值非固定的，每次重新登录会返回新的，数据库记得实时更新wid）** |
| base64 | string | 图片二维码 |

### POST /member/login

- operationId: `deng_lu_deng_lu_wei_kong_ping_tai_di_yi_bu`
- title: 登录E云平台（第一步）
- doc: `docs/api/api-wen-dang2/deng-lu/deng-lu-wei-kong-ping-tai-di-yi-bu.md`
- requestUrl (as documented): `http://域名地址/member/login`

**Headers（文档提取）**
- Content-Type: application/json

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| account | 是 | string | **开发者**账号 |
| password | 是 | string | **开发者**密码 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| **Authorization** | string | 授权密钥，生成后永久有效 |
| callbackUrl | string | 消息回调地址 |
| status | string | 状态（0：正常，1：冻结，2：到期） |

### POST /secondLogin

- operationId: `deng_lu_er_ci_deng_lu`
- title: 弹框登录
- doc: `docs/api/api-wen-dang2/deng-lu/er-ci-deng-lu.md`
- requestUrl (as documented): `http://域名地址/secondLogin`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wcId | 是 | string | 微信id（登录接口返回的wcId） |
| ttuid | 否 | string | 网络类型2，若上次登录使用ttuid，本参数则必传，反之则不传 |
| aid | 否 | string |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| **wId** | string | 登录实例标识, **登录成功后wId会变更，记得更新** |
| wcId | string | 微信id |
| nickName | string | 昵称 |
| headUrl | string | 头像url |
| wAccount | string | 手机上显示的微信号 |
| sex | int | 性别 |
| status | string | 3 扫码登录成功 |

## 模块：`hao-you-cao-zuo`

### POST /acceptUser

- operationId: `hao_you_cao_zuo_acceptUser`
- title: 同意添加好友
- doc: `docs/api/api-wen-dang2/hao-you-cao-zuo/acceptUser.md`
- requestUrl (as documented): `http://域名地址/acceptUser`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| v1 | 是 | string | v1（从消息回调中取） |
| v2 | 是 | string | v2（从消息回调中取） |
| type | 是 | int | 取回调中的scene来源 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |

### POST /addUser

- operationId: `hao_you_cao_zuo_addFriend`
- title: 添加好友
- doc: `docs/api/api-wen-dang2/hao-you-cao-zuo/addFriend.md`
- requestUrl (as documented): `http://域名地址/addUser`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| v1 | 是 | string | v1 从[搜索好友接口](serchUser.html)获取 |
| v2 | 是 | string | v2 从[搜索好友接口](serchUser.html)获取 |
| type | 是 | int |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |

### POST /checkZombie

- operationId: `hao_you_cao_zuo_checkZombie`
- title: 检测好友状态
- doc: `docs/api/api-wen-dang2/hao-you-cao-zuo/checkZombie.md`
- requestUrl (as documented): `http://域名地址/checkZombie`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| wcId | 是 | String | 好友微信id，多个已","分隔,每次最多支持个20 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /delContact

- operationId: `hao_you_cao_zuo_shan_chu_hao_you`
- title: 删除好友
- doc: `docs/api/api-wen-dang2/hao-you-cao-zuo/shan-chu-hao-you.md`
- requestUrl (as documented): `http://域名地址/delContact`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 微信实列ID |
| wcId | 是 | String | 需删除的微信id |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |

### POST /getContact

- operationId: `hao_you_cao_zuo_queryUserInfo`
- title: 获取联系人信息
- doc: `docs/api/api-wen-dang2/hao-you-cao-zuo/queryUserInfo.md`
- requestUrl (as documented): `http://域名地址/getContact`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| wcId | 是 | String | 好友微信id/群id,多个好友/群 以","分隔每次最多支持20个微信/群号,本接口每次调用请随机间隔300ms-800ms之间 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /getImAddressList

- operationId: `hao_you_cao_zuo_getImAddressList`
- title: 获取企微联系人列表
- doc: `docs/api/api-wen-dang2/hao-you-cao-zuo/getImAddressList.md`
- requestUrl (as documented): `http://域名地址/getImAddressList`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /getOpenImContact

- operationId: `hao_you_cao_zuo_getOpenImContact`
- title: 获取企微联系人信息
- doc: `docs/api/api-wen-dang2/hao-you-cao-zuo/getOpenImContact.md`
- requestUrl (as documented): `http://域名地址/getOpenImContact`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| wcId | 是 | String | 企微好友微信id |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /getQrCode

- operationId: `hao_you_cao_zuo_huo_qu_zi_ji_de_er_wei_ma`
- title: 获取我的二维码
- doc: `docs/api/api-wen-dang2/hao-you-cao-zuo/huo-qu-zi-ji-de-er-wei-ma.md`
- requestUrl (as documented): `http://域名地址/getQrCode`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /modifyRemark

- operationId: `hao_you_cao_zuo_xiu_gai_hao_you_bei_zhu`
- title: 修改好友备注
- doc: `docs/api/api-wen-dang2/hao-you-cao-zuo/xiu-gai-hao-you-bei-zhu.md`
- requestUrl (as documented): `http://域名地址/modifyRemark`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 好友微信id |
| remark | 是 | string | 好友备注 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |

### POST /searchUser

- operationId: `hao_you_cao_zuo_serchUser`
- title: 搜索联系人
- doc: `docs/api/api-wen-dang2/hao-you-cao-zuo/serchUser.md`
- requestUrl (as documented): `http://域名地址/searchUser`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| wcId | 是 | String | 微信号/手机号 (不支持微信id搜索) |

### POST /sendHeadImage

- operationId: `hao_you_cao_zuo_she_zhi_ge_ren_tou_tou_xiang`
- title: 设置个人头头像
- doc: `docs/api/api-wen-dang2/hao-you-cao-zuo/she-zhi-ge-ren-tou-tou-xiang.md`
- requestUrl (as documented): `http://域名地址/sendHeadImage`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: Authorization值（登录获取二维码信息接口中返回的认证信息值）

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| path | 是 | string | 图片url链接 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |

### POST /setDisturb

- operationId: `hao_you_cao_zuo_setDisturb`
- title: 设置聊天免打扰
- doc: `docs/api/api-wen-dang2/hao-you-cao-zuo/setDisturb.md`
- requestUrl (as documented): `http://域名/setDisturb`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| chatRoomId | 是 | String | 好友id/群id |
| type | 是 | int | 0：开启 1：关闭 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /setFriendPemission

- operationId: `hao_you_cao_zuo_setFriendPermission`
- title: 设置好友权限
- doc: `docs/api/api-wen-dang2/hao-you-cao-zuo/setFriendPermission.md`
- requestUrl (as documented): `http://域名地址/setFriendPemission`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 微信实列ID |
| wcId | 是 | String | 好友微信id |
| type | 是 | int | 1:正常 2:仅聊天 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |

### POST /setTop

- operationId: `hao_you_cao_zuo_setTop`
- title: 设置聊天置顶
- doc: `docs/api/api-wen-dang2/hao-you-cao-zuo/setTop.md`
- requestUrl (as documented): `http://域名/setTop`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| wcId | 是 | String | 好友id/群id |
| operType | 是 | int | 0：取消 1：置顶 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /userPrivacySettings

- operationId: `hao_you_cao_zuo_userPrivacySettings`
- title: 添加隐私设置
- doc: `docs/api/api-wen-dang2/hao-you-cao-zuo/userPrivacySettings.md`
- requestUrl (as documented): `http://域名地址/userPrivacySettings`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| privacyType | 是 | int |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

## 模块：`peng-you-quan`

### POST /asynSnsSendVideo

- operationId: `peng_you_quan_asynSnsSendVideo`
- title: 异步发送视频朋友圈
- doc: `docs/api/api-wen-dang2/peng-you-quan/asynSnsSendVideo.md`
- requestUrl (as documented): `http://域名地址/asynSnsSendVideo`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| content | 是 | String | 文本内容 |
| videoPath | 是 | String | 视频链接URL 最大支持20M且30秒内 |
| thumbPath | 是 | String | 视频封面URL 最大支持2M内 |
| groupUser | 否 | String | 对谁可见（传微信号,多个用,分隔） |
| blackList | 否 | String | 对谁不可见（传微信号,多个用.分隔） |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | String | 反馈信息 |
| data |  |  |
| asynId | String | 异步发送视频朋友圈asynId，可用此参数[获取发送视频朋友圈结果](getAsynSnsSendVideoRes.html) |

### POST /deleteSns

- operationId: `peng_you_quan_deleteSns`
- title: 删除朋友圈
- doc: `docs/api/api-wen-dang2/peng-you-quan/deleteSns.md`
- requestUrl (as documented): `http://域名地址/deleteSns`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| id | 是 | String | 朋友圈id |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | String | 反馈信息 |

### POST /downloadSnsVideo

- operationId: `peng_you_quan_downloadSnsVideo`
- title: 下载朋友圈视频
- doc: `docs/api/api-wen-dang2/peng-you-quan/downloadSnsVideo.md`
- requestUrl (as documented): `http://域名地址/downloadSnsVideo`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| content | 是 | String | 通过获取某条朋友圈详细内容接口\[/getSnsObject\]返回的xml |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| message | String | 反馈信息 |

### POST /forwardSns

- operationId: `peng_you_quan_forwardSns`
- title: 转发朋友圈
- doc: `docs/api/api-wen-dang2/peng-you-quan/forwardSns.md`
- requestUrl (as documented): `http://域名地址/forwardSns`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| content | 是 | String | 收到的xml |
| blackList | 否 | String | 对谁不可见（传微信id,多个用,分隔） |
| withUserList | 否 | String | 对谁可见 （传微信id,多个用,分隔） |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | String | 反馈信息 |
| id | String | 朋友圈ID |
| userName | String | 微信id |
| createTime | String | 时间 |
| objectDesc | JSONObject | 朋友圈内容 |
| xml | String | 朋友圈xml |
| len | int | xml 长度 |
| commentId | int | 评论标识 |
| replyCommentId | int | 回复评论标识 |
| deleteFlag | int | 删除标识 |
| isNotRichText | int | 是否试富文本 |
| content | String | 评论内容 |
| commentId | int | 评论ID |
| snsLikes | JSONArray | 点赞用户列表 |
| userName | String | 微信id |
| nickName | String | 昵称 |
| type | int | 点赞类型 |
| createTime | int | 点赞时间 |

### POST /getAsynSnsSendVideoRes

- operationId: `peng_you_quan_getAsynSnsSendVideoRes`
- title: 获取发送视频朋友圈结果
- doc: `docs/api/api-wen-dang2/peng-you-quan/getAsynSnsSendVideoRes.md`
- requestUrl (as documented): `http://域名地址/getAsynSnsSendVideoRes`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| asynId | 是 | String | 异步发送视频朋友圈返回的asynId |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | String | 反馈信息 |
| data |  |  |
| data.asynId | String | 异步发送视频朋友圈asynId |
| data.type | int | 发送状态。0：发送中、1：发送完成、2：发送失败 |
| data.id | string | 朋友圈id |
| data.userName | string | 发送微信id |
| data.createTime | long | 发送时间 |
| data.objectDesc | string | 朋友圈文字 |
| data.des | string | 描述 |

### POST /getCircle

- operationId: `peng_you_quan_getCircle`
- title: 获取朋友圈
- doc: `docs/api/api-wen-dang2/peng-you-quan/getCircle.md`
- requestUrl (as documented): `http://域名地址/getCircle`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回 **参数：**

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| firstPageMd5 | 是 | String |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | String | 反馈信息 |
| data |  |  |
| id | String | 朋友圈ID |
| userName | String | 微信id |
| nickName | String | 昵称 |
| createTime | String | 时间 |
| objectDesc | JSONObject | 朋友圈内容 |
| xml | String | 朋友圈xml |
| len | int | xml 长度 |
| snsComments | JSONArray | 评论用户列表 |
| userName | String | 微信id |
| nickName | String | 昵称 |
| type | int | 评论类型 |
| createTime | int | 评论时间 |
| commentId | int | 评论标识 |
| replyCommentId | int | 回复评论标识 |
| deleteFlag | int | 删除标识 |
| isNotRichText | int | 是否试富文本 |
| content | String | 评论内容 |
| commentId | int | 评论ID |
| snsLikes | JSONArray | 点赞用户列表 |
| userName | String | 微信id |
| nickName | String | 昵称 |
| type | int | 点赞类型 |
| createTime | int | 点赞时间 |

### POST /getFriendCircle

- operationId: `peng_you_quan_getFriendCircle`
- title: 获取某个好友的朋友圈
- doc: `docs/api/api-wen-dang2/peng-you-quan/getFriendCircle.md`
- requestUrl (as documented): `http://域名地址/getFriendCircle`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| wcId | 是 | String | 微信id |
| firstPageMd5 | 是 | String | 首页传:""，第2页及以后传返回的firstPageMd5 （PS：firstPageMd5为null情况下，则用上次不为null的值） |
| maxId | 是 | long | 首页传：0（PS：第2页及以后用返回数据最后一个条目的id） |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | String | 反馈信息 |
| data |  |  |
| id | String | 朋友圈ID |
| userName | String | 微信id |
| createTime | String | 时间 |
| objectDesc | JSONObject | 朋友圈内容 |
| xml | String | 朋友圈xml |
| len | int | xml 长度 |
| commentId | int | 评论标识 |
| replyCommentId | int | 回复评论标识 |
| deleteFlag | int | 删除标识 |
| isNotRichText | int | 是否试富文本 |
| content | String | 评论内容 |
| commentId | int | 评论ID |
| snsLikes | JSONArray | 点赞用户列表 |
| userName | String | 微信id |
| nickName | String | 昵称 |
| type | int | 点赞类型 |
| createTime | int | 点赞时间 |
| firstPageMd5 | String |  |

### POST /getSnsObject

- operationId: `peng_you_quan_getSnsObject`
- title: 获取某条朋友圈详细内容
- doc: `docs/api/api-wen-dang2/peng-you-quan/getSnsObject.md`
- requestUrl (as documented): `http://域名地址/getSnsObject`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| wcId | 是 | String | 好友微信id |
| id | 是 | String | 朋友圈标识 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | String | 反馈信息 |
| data |  |  |
| id | String | 朋友圈ID |
| userName | String | 微信id |
| nickName | String | 昵称 |
| createTime | String | 时间 |
| objectDesc | JSONObject | 朋友圈内容 |
| xml | String | 朋友圈xml |
| len | int | xml 长度 |
| snsComments | JSONArray | 评论用户列表 |
| userName | String | 微信id |
| nickName | String | 昵称 |
| type | int | 评论类型 |
| createTime | int | 评论时间 |
| commentId | int | 评论标识 |
| replyCommentId | int | 回复评论标识 |
| deleteFlag | int | 删除标识 |
| isNotRichText | int | 是否试富文本 |
| content | String | 评论内容 |
| commentId | int | 评论ID |
| snsLikes | JSONArray | 点赞用户列表 |
| userName | String | 微信id |
| nickName | String | 昵称 |
| type | int | 点赞类型 |
| createTime | int | 点赞时间 |

### POST /snsCancelPraise

- operationId: `peng_you_quan_snsCancelPraise`
- title: 取消点赞
- doc: `docs/api/api-wen-dang2/peng-you-quan/snsCancelPraise.md`
- requestUrl (as documented): `http://域名地址/snsCancelPraise`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| id | 是 | String | 朋友圈id |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | String | 反馈信息 |

### POST /snsComment

- operationId: `peng_you_quan_snsComment`
- title: 朋友圈评论
- doc: `docs/api/api-wen-dang2/peng-you-quan/snsComment.md`
- requestUrl (as documented): `http://域名地址/snsComment`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| id | 是 | String | 朋友圈标识 |
| replyCommentId | 是 | int | 评论标识（回复评论） |
| content | 是 | String | 内容 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | int | 1000成功，1001失败 |
| msg | String | 反馈信息 |

### POST /snsCommentDel

- operationId: `peng_you_quan_snsCommentDel`
- title: 删除某条朋友圈的某条评论
- doc: `docs/api/api-wen-dang2/peng-you-quan/snsCommentDel.md`
- requestUrl (as documented): `http://域名地址/snsCommentDel`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| id | 是 | String | 朋友圈id |
| commentId | 是 | int | 评论id |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | String | 反馈信息 |

### POST /snsPraise

- operationId: `peng_you_quan_snsPraise`
- title: 朋友圈点赞
- doc: `docs/api/api-wen-dang2/peng-you-quan/snsPraise.md`
- requestUrl (as documented): `http://域名地址/snsPraise`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| id | 是 | String | 朋友圈Id |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | String | 反馈信息 |

### POST /snsPrivacySettings

- operationId: `peng_you_quan_snsPrivacySettings`
- title: 朋友圈权限设置
- doc: `docs/api/api-wen-dang2/peng-you-quan/snsPrivacySettings.md`
- requestUrl (as documented): `http://域名地址/snsPrivacySettings`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| type | 是 | int |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | String | 反馈信息 |

### POST /snsSend

- operationId: `peng_you_quan_snsSend`
- title: 发送文字朋友圈消息
- doc: `docs/api/api-wen-dang2/peng-you-quan/snsSend.md`
- requestUrl (as documented): `http://域名地址/snsSend`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回 **参数：**

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| content | 是 | String | 文本内容 |
| groupUser | 否 | String | 对谁可见（传微信id,多个用,分隔） |
| blackList | 否 | String | 对谁不可见（传微信id,多个用,分隔） |
| groupUserLabelIds | 否 | String | 对谁可见（传标签id,多个用,分隔） |
| blackListLabelIds | 否 | String | 对谁不可见（传标签id,多个用,分隔） |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | String | 反馈信息 |
| data |  |  |
| id | String | ID |
| userName | String | 微信id |
| createTime | String | 发送时间 |
| objectDesc | String | 内容 |

### POST /snsSendImage

- operationId: `peng_you_quan_snsSendImage`
- title: 发送图片朋友圈消息
- doc: `docs/api/api-wen-dang2/peng-you-quan/snsSendImage.md`
- requestUrl (as documented): `http://域名地址/snsSendImage`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| content | 是 | String | 文本内容 |
| paths | 是 | String | 图片url(多个用;分隔 单张图片最大3M以内,必须是png格式) |
| groupUser | 否 | String | 对谁可见（传微信id,多个用,分隔） |
| blackList | 否 | String | 对谁不可见（传微信id,多个用,分隔） |
| groupUserLabelIds | 否 | String | 对谁可见（传标签id,多个用,分隔） |
| blackListLabelIds | 否 | String | 对谁不可见（传标签id,多个用,分隔） |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | String | 反馈信息 |
| data |  |  |
| id | String | ID |
| userName | String | 微信id |
| createTime | String | 发送时间 |
| objectDesc | String | 内容 |

### POST /snsSendUrl

- operationId: `peng_you_quan_snsSendUrl`
- title: 发送链接朋友圈消息
- doc: `docs/api/api-wen-dang2/peng-you-quan/snsSendUrl.md`
- requestUrl (as documented): `http://域名地址/snsSendUrl`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| content | 是 | String | 文本内容 |
| title | 是 | String | 标题 |
| description | 是 | String | 描述 |
| url | 是 | String | url |
| thumbUrl | 是 | String | 缩略图url |
| groupUser | 否 | String | 对谁可见（传微信id,多个用,分隔） |
| blackList | 否 | String | 对谁不可见（传微信id,多个用,分隔） |
| groupUserLabelIds | 否 | String | 对谁可见（传标签id,多个用,分隔） |
| blackListLabelIds | 否 | String | 对谁不可见（传标签id,多个用,分隔） |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | String | 反馈信息 |
| data |  |  |
| id | String | ID |
| userName | String | 微信id |
| createTime | String | 发送时间 |
| objectDesc | String | 内容 |

### POST /snsSetAsPrivacy

- operationId: `peng_you_quan_snsSetAsPrivacy`
- title: 设置某条朋友圈为隐私
- doc: `docs/api/api-wen-dang2/peng-you-quan/snsSetAsPrivacy.md`
- requestUrl (as documented): `http://域名地址/snsSetAsPrivacy`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| id | 是 | String | 朋友圈id |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | String | 反馈信息 |

### POST /snsSetPublic

- operationId: `peng_you_quan_snsSetPublic`
- title: 设置某条朋友圈为公开
- doc: `docs/api/api-wen-dang2/peng-you-quan/snsSetPublic.md`
- requestUrl (as documented): `http://域名地址/snsSetPublic`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| id | 是 | String | 朋友圈id |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | String | 反馈信息 |

## 模块：`qun-cao-zuo`

### POST /acceptUrl

- operationId: `qun_cao_zuo_acceptMemberGroup`
- title: 自动通过群（url）
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/acceptMemberGroup.md`
- requestUrl (as documented): `http://域名地址/acceptUrl`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: Authorization值（登录获取二维码信息接口中返回的认证信息值）

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| url | 是 | string | 原始 url，好友发送的入群邀请卡片信息链接(回调中取) |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |

### POST /addChatRoomMember

- operationId: `qun_cao_zuo_addGroupMember`
- title: 添加群成员
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/addGroupMember.md`
- requestUrl (as documented): `http://域名地址/addChatRoomMember`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| chatRoomId | 是 | String | 群号 |
| userList | 是 | String | 群成员微信id，多个已 "," 分割 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |

### POST /addChatRoomMemberVerify

- operationId: `qun_cao_zuo_addChatRoomMemberVerify`
- title: 邀请群成员（开启群验证）
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/addChatRoomMemberVerify.md`
- requestUrl (as documented): `http://域名/addChatRoomMemberVerify`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| chatRoomId | 是 | String | 群id |
| userList | 是 | number | 邀请好友的id |
| reason | 是 | String | 邀请理由（管理员查看，不得为空） |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /addRoomMemberFriend

- operationId: `qun_cao_zuo_addRoomMemberFriend`
- title: 添加群成员为好友
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/addRoomMemberFriend.md`
- requestUrl (as documented): `http://域名/addRoomMemberFriend`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| chatRoomId | 是 | String | 群id |
| memberWcId | 是 | String | 群成员的wcId |
| content | 否 | String | 申请消息 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /agreeAddChatRoomMember

- operationId: `qun_cao_zuo_agreeAddChatRoomMember`
- title: 群管理确认入群邀请
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/agreeAddChatRoomMember.md`
- requestUrl (as documented): `http://域名/agreeAddChatRoomMember`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| chatRoomId | 是 | String | 群id |
| newMsgId | 是 | number | 入群邀请回调返回newmMsgid |
| xml | 是 | String | 入群邀请的回调xml |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /createChatroom

- operationId: `qun_cao_zuo_chuang_jian_wei_xin_qun`
- title: 创建微信群
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/chuang-jian-wei-xin-qun.md`
- requestUrl (as documented): `http://域名地址/createChatroom`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| userList | 是 | String | 群成员微信id，多个已 "," 分割，（必须传输2个微信id以上才可创建群聊） |
| topic | 否 | String | 群名 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /deleteChatRoomMember

- operationId: `qun_cao_zuo_delGroupMember`
- title: 删除群成员
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/delGroupMember.md`
- requestUrl (as documented): `http://域名地址/deleteChatRoomMember`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| chatRoomId | 是 | String | 群号 |
| userList | 是 | String | 群成员微信id，多个已 "," 分割 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |

### POST /getChatRoomInfo

- operationId: `qun_cao_zuo_queryGroupDetail`
- title: 获取群信息
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/queryGroupDetail.md`
- requestUrl (as documented): `http://域名地址/getChatRoomInfo`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| chatRoomId | 是 | String | 群号 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /getChatRoomMember

- operationId: `qun_cao_zuo_queryGroupList`
- title: 获取群成员
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/queryGroupList.md`
- requestUrl (as documented): `http://域名地址/getChatRoomMember`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| chatRoomId | 是 | String | 群号 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /getChatRoomMemberInfo

- operationId: `qun_cao_zuo_queryGroupMemberDetail`
- title: 获取群成员详情
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/queryGroupMemberDetail.md`
- requestUrl (as documented): `http://域名/getChatRoomMemberInfo`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| chatRoomId | 是 | String | 群号 |
| userList | 是 | String |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string |  |

### POST /getGroupQrCode

- operationId: `qun_cao_zuo_queryGroupQrCode`
- title: 获取群二维码
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/queryGroupQrCode.md`
- requestUrl (as documented): `http://域名地址/getGroupQrCode`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| chatRoomId | 是 | String | 群号 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /inviteChatRoomMember

- operationId: `qun_cao_zuo_inviteGroupMember`
- title: 邀请群成员（40人以上）
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/inviteGroupMember.md`
- requestUrl (as documented): `http://域名地址/inviteChatRoomMember`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| chatRoomId | 是 | String | 群号 |
| userList | 是 | String | 群成员微信id，多个已 "," 分割 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |

### POST /modifyGroupName

- operationId: `qun_cao_zuo_updateGroupName`
- title: 修改群名称
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/updateGroupName.md`
- requestUrl (as documented): `http://域名地址/modifyGroupName`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| chatRoomId | 是 | String | 群号 |
| content | 是 | String | 群名 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /modifyGroupRemark

- operationId: `qun_cao_zuo_updateGroupRemark`
- title: 修改群备注
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/updateGroupRemark.md`
- requestUrl (as documented): `http://域名地址/modifyGroupRemark`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| chatRoomId | 是 | String | 群号 |
| content | 是 | String | 群名 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /operateChatRoom

- operationId: `qun_cao_zuo_operateChatRoom`
- title: 群管理操作
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/operateChatRoom.md`
- requestUrl (as documented): `http://域名/operateChatRoom`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| chatRoomId | 是 | String | 群号 |
| wcId | 是 | String | 群成员微信id，多个用 "," 分割 |
| type | 是 | int | 1：添加群管理（可添加多个微信id） 2：删除群管理（可删除多个） 3：转让（只能转让一个微信号） |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /quitChatRoom

- operationId: `qun_cao_zuo_quitGroup`
- title: 退出群聊
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/quitGroup.md`
- requestUrl (as documented): `http://域名地址/quitChatRoom`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| chatRoomId | 是 | string | 群id |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |

### POST /roomAppTodo

- operationId: `qun_cao_zuo_roomAppTodo`
- title: 设置群待办消息
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/roomAppTodo.md`
- requestUrl (as documented): `http://域名/roomAppTodo`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| chatRoomId | 是 | String | 群id |
| newMsgId | 是 | int | 小程序的消息id(小程序消息回调返回newMsgid) |
| title | 是 | 小程序标题 | 小程序消息回调中取 |
| pagePath | 是 | 小程序跳转地址 | 小程序消息回调中取 |
| userName | 是 | 小程序id | 小程序回调中取 |
| sendWcId | 是 | 原小程序的发送者id | 小程序回调中取 |
| sign | 否 | int | 撤回传，设置待办成功后返回本字段 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /roomTodo

- operationId: `qun_cao_zuo_roomTodo`
- title: 设置群待办消息
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/roomTodo.md`
- requestUrl (as documented): `http://域名/roomTodo`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| chatRoomId | 是 | String | 群id |
| newMsgId | 是 | int | 群公告的消息id(设置群公告成功后，回调返回newMsgId) |
| operType | 是 | int | 0:设置群待办 1:撤回群待办 |
| sign | 否 | int | 撤回传，设置待办成功后返回本字段 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /scanJoinRoom

- operationId: `qun_cao_zuo_scanJoinRoom`
- title: 扫码入群
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/scanJoinRoom.md`
- requestUrl (as documented): `http://域名地址/scanJoinRoom`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| url | 是 | string | 群二维码url（二维码解析后的url） |
| type | 否 | int |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |

### POST /setChatRoomAnnouncement

- operationId: `qun_cao_zuo_setGroupAnnounct`
- title: 设置群公告
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/setGroupAnnounct.md`
- requestUrl (as documented): `http://域名地址/setChatRoomAnnouncement`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| chatRoomId | 是 | String | 群号 |
| content | 是 | String | 内容 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /showInAddressBook

- operationId: `qun_cao_zuo_saveGroup`
- title: 群保存|取消到通讯录
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/saveGroup.md`
- requestUrl (as documented): `http://域名地址/showInAddressBook`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| chatRoomId | 是 | String | 群号 |
| flag | 是 | int |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /updateIInChatRoomNickName

- operationId: `qun_cao_zuo_updateIInChatRoomNickName`
- title: 修改我在某群的昵称
- doc: `docs/api/api-wen-dang2/qun-cao-zuo/updateIInChatRoomNickName.md`
- requestUrl (as documented): `http://域名/updateIInChatRoomNickName`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string |  |

## 模块：`shipinhao`

### POST /createFinder

- operationId: `shipinhao_createFinder`
- title: 创建视频号
- doc: `docs/api/api-wen-dang2/shipinhao/createFinder.md`
- requestUrl (as documented): `http://域名/createFinder`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| nickName | 是 | String | 视频号名称 |
| headImgUrl | 是 | String | 视频号头像 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /finder/getContactDetails

- operationId: `shipinhao_getContactDetails`
- title: 获取私信联系人信息
- doc: `docs/api/api-wen-dang2/shipinhao/getContactDetails.md`
- requestUrl (as documented): `http://域名/finder/getContactDetails`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| meUserName | 是 | String | 自己的用户编码（获取个人主页接口返回的userName） |
| meRoleType | 是 | int | 自己的角色类型，根据角色关注（获取个人主页接口返回的roleType） |
| contactUserName | 是 | String | 私信联系人的username |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /finder/getFollowList

- operationId: `shipinhao_getFollowList`
- title: 获取关注列表
- doc: `docs/api/api-wen-dang2/shipinhao/getFollowList.md`
- requestUrl (as documented): `http://域名/finder/getFollowList`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| lastBuff | 否 | String | 首次传空，后续传接口返回的lastBuffer |
| myUserName | 是 | String | 自己的用户编码（获取个人主页接口返回的userName） |
| myRoleType | 是 | int | 自己的角色类型，根据角色关注（获取个人主页接口返回的roleType） |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /finder/getLikeAndFavList

- operationId: `shipinhao_getLikeAndFavList`
- title: 获取赞和收藏的视频列表
- doc: `docs/api/api-wen-dang2/shipinhao/getLikeAndFavList.md`
- requestUrl (as documented): `http://域名/finder/getLikeAndFavList`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| lastBuffer | 否 | String | 首次传空，后续传接口返回的lastBuffer |
| myUserName | 是 | String | 自己的用户编码（获取个人主页接口返回的userName） |
| myRoleType | 是 | int | 自己的角色类型，根据角色关注（获取个人主页接口返回的roleType） |
| flag | 是 | int | 视频类型，7:全部 1:红心 2:大拇指 4:收藏 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /finder/getMentionList

- operationId: `shipinhao_getMentionList`
- title: 消息列表
- doc: `docs/api/api-wen-dang2/shipinhao/getMentionList.md`
- requestUrl (as documented): `http://域名/finder/getMentionList`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| lastBuff | 是 | String | 翻页的key，首次传空，翻页传接口返回的lastBuff |
| myUserName | 是 | String | 自己的用户编码（获取个人主页接口返回的userName） |
| myRoleType | 是 | int | 自己的角色类型，根据角色关注（获取个人主页接口返回的roleType） |
| reqScene | 是 | int | 消息类型，3是点赞 4是评论 5是关注 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /finder/getQrCode

- operationId: `shipinhao_getQrCode`
- title: 获取我的视频号二维码
- doc: `docs/api/api-wen-dang2/shipinhao/getQrCode.md`
- requestUrl (as documented): `http://域名/finder/getQrCode`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| meUserName | 是 | String | 自己的用户编码（获取个人主页接口返回的userName） |
| meRoleType | 是 | int | 自己的角色类型，根据角色关注（获取个人主页接口返回的roleType） |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /finderBrowse

- operationId: `shipinhao_finderBrowse`
- title: 浏览
- doc: `docs/api/api-wen-dang2/shipinhao/finderBrowse.md`
- requestUrl (as documented): `http://域名/finderBrowse`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| objectId | 是 | bigint | 视频号作品id |
| objectNonceId | 是 | String | 视频号作品nonceId |
| sessionBuffer | 是 | String | 通过获取用户主页返回的sessionBuffer |
| myUserName | 是 | String | 自己的用户编码（获取个人主页接口返回的userName） |
| myRoleType | 是 | int | 自己的角色类型，根据角色关注（获取个人主页接口返回的roleType） |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /finderComment

- operationId: `shipinhao_finderComment`
- title: 评论
- doc: `docs/api/api-wen-dang2/shipinhao/finderComment.md`
- requestUrl (as documented): `http://域名/finderComment`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| content | 是 | String | 评论内容 |
| id | 是 | bigint | 视频号作品id |
| objectNonceId | 是 | String | 视频号作品nonceId |
| type | 是 | int |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /finderCommentDetails

- operationId: `shipinhao_finderCommentDetails`
- title: 获取评论列表
- doc: `docs/api/api-wen-dang2/shipinhao/finderCommentDetails.md`
- requestUrl (as documented): `http://域名/finderCommentDetails`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| id | 是 | bigint | 视频号作品id |
| pageCode | 是 | String | 分页code，首次传空，后续传接口返回的 |
| sessionBuffer | 是 | String | 通过获取用户主页返回的sessionBuffer |
| refCommentId | 是 | String | 默认为0 |
| rootCommentId | 是 | bigint | 获取评论的回复详情时传上级评论的ID |
| nonceId | 是 | String | 视频号作品nonceId |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /finderFollow

- operationId: `shipinhao_finderFollow`
- title: 关注
- doc: `docs/api/api-wen-dang2/shipinhao/finderFollow.md`
- requestUrl (as documented): `http://域名/finderFollow`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| userName | 是 | String | 视频号用户的编码（搜索接口返回的userName） |
| meUserName | 是 | String | 自己的用户编码（获取个人主页接口返回的userName） |
| meRoleType | 是 | int | 自己的角色类型，根据角色关注（获取个人主页接口返回的roleType） |
| type | 是 | int |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /finderHome

- operationId: `shipinhao_finderHome`
- title: 获取个人主页
- doc: `docs/api/api-wen-dang2/shipinhao/finderHome.md`
- requestUrl (as documented): `http://域名/finderHome`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /finderIdFav

- operationId: `shipinhao_finderIdFav`
- title: 点赞
- doc: `docs/api/api-wen-dang2/shipinhao/finderIdFav.md`
- requestUrl (as documented): `http://域名/finderIdFav`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| id | 是 | bigint | 视频号作品id |
| nonceId | 是 | String | 视频号作品nonceId |
| type | 是 | int |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /finderIdLike

- operationId: `shipinhao_finderIdLike`
- title: 小红心
- doc: `docs/api/api-wen-dang2/shipinhao/finderIdLike.md`
- requestUrl (as documented): `http://域名/finderIdLike`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| id | 是 | bigint | 视频号作品id |
| commentId | 是 | bigint | 评论的id |
| nonceId | 是 | String | 视频号作品nonceId |
| type | 是 | int | 视频操作 3喜欢 4不喜欢 评论操作 1喜欢 2不喜欢 |
| sessionBuffer | 是 | String | 通过获取用户主页返回的sessionBuffer |
| toUserName | 是 | String | 作者的username |
| meUserName | 是 | String | 自己的用户编码（获取个人主页接口返回的userName） |
| meRoleType | 是 | int | 自己的角色类型，根据角色关注（获取个人主页接口返回的roleType） |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /finderPublish

- operationId: `shipinhao_finderPublish`
- title: 发布视频号
- doc: `docs/api/api-wen-dang2/shipinhao/finderPublish.md`
- requestUrl (as documented): `http://域名/finderPublish`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| myUserName | 是 | String | 自己的用户编码 |
| videoUrl | 是 | String | 视频链接 |
| videoThumbUrl | 是 | String | 封面链接 |
| videoWidth | 是 | int | 视频宽度 |
| videoHeight | 是 | int | 视频高度 |
| videoPlayLen | 是 | int | 视频播放时长，单位秒 |
| title | 是 | String | 标题 |
| topic | 是 | String\[\] | 话题 |
| videoCdn | 否 | JSONObject | 通过“上传视频号视频”接口获取 |
| videoCdn.fileUrl | 是 | String | 通过“上传视频号视频”接口获取 |
| videoCdn.thumbUrl | 是 | String | 通过“上传视频号视频”接口获取 |
| videoCdn.mp4Identify | 是 | String | 通过“上传视频号视频”接口获取 |
| videoCdn.fileSize | 是 | int | 通过“上传视频号视频”接口获取 |
| videoCdn.thumbMd5 | 是 | String | 通过“上传视频号视频”接口获取 |
| videoCdn.fileKey | 是 | String | 通过“上传视频号视频”接口获取 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /finderUpload

- operationId: `shipinhao_finderUpload`
- title: 上传视频号视频
- doc: `docs/api/api-wen-dang2/shipinhao/finderUpload.md`
- requestUrl (as documented): `http://域名/finderUpload`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| videoUrl | 是 | String | 视频链接 |
| imgUrl | 是 | String | 视频封面图片链接 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /finderUserHome

- operationId: `shipinhao_finderUserHome`
- title: 获取用户主页
- doc: `docs/api/api-wen-dang2/shipinhao/finderUserHome.md`
- requestUrl (as documented): `http://域名/finderUserHome`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| userName | 是 | String | 视频号用户的编码（搜索接口返回的userName） |
| pageCode | 否 | String | 分页参数，首次传空，获取下一页时传响应中返回的pageCode |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /getSessionId

- operationId: `shipinhao_getSessionId`
- title: 获取私信SessionId
- doc: `docs/api/api-wen-dang2/shipinhao/getSessionId.md`
- requestUrl (as documented): `http://域名/getSessionId`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| toUserName | 是 | String | 视频号用户的编码 |
| myUserName | 是 | String | 自己的用户编码 |
| type | 是 | int |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /modFinderProfile

- operationId: `shipinhao_modFinderProfile`
- title: 修改视频号资料
- doc: `docs/api/api-wen-dang2/shipinhao/modFinderProfile.md`
- requestUrl (as documented): `http://域名/modFinderProfile`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| meUserName | 是 | String | 自己的用户编码（获取个人主页接口返回的userName） |
| meRoleType | 是 | int | 自己的角色类型，根据角色关注（获取个人主页接口返回的roleType） |
| nickName | 是 | String | 视频号昵称 |
| signature | 是 | String | 视频号简介 |
| headImgUrl | 是 | String | 视频号头像链接 |
| country | 是 | String | 国家 |
| province | 是 | String | 省份 |
| city | 是 | String | 城市 |
| sex | 是 | int | 性别 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /newSearchFinder

- operationId: `shipinhao_searchFinder`
- title: 搜索视频号
- doc: `docs/api/api-wen-dang2/shipinhao/searchFinder.md`
- requestUrl (as documented): `http://域名/newSearchFinder`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| content | 是 | String | 搜索内容 |
| type | 是 | int |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /privateSend

- operationId: `shipinhao_privateSend`
- title: 私信文字
- doc: `docs/api/api-wen-dang2/shipinhao/privateSend.md`
- requestUrl (as documented): `http://域名/privateSend`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| toUserName | 是 | String | 视频号用户的编码 |
| myUserName | 是 | String | 当前微信的用户编码 |
| sessionId | 是 | String | 通过/getSessionId接口获取 |
| content | 是 | String | 私信内容 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /privateSendImg

- operationId: `shipinhao_privateSendImg`
- title: 私信图片
- doc: `docs/api/api-wen-dang2/shipinhao/privateSendImg.md`
- requestUrl (as documented): `http://域名/privateSendImg`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| toUserName | 是 | String | 视频号用户的编码 |
| sessionId | 是 | String | 通过/getSessionId接口获取 |
| imgUrl | 是 | String | 图片地址 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

### POST /scanFinderHelper

- operationId: `shipinhao_scanFinderHelper`
- title: 登录视频号助手
- doc: `docs/api/api-wen-dang2/shipinhao/scanFinderHelper.md`
- requestUrl (as documented): `http://域名/scanFinderHelper`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 登录实例标识 |
| url | 是 | String | 视频号助手官方二维码解析的地址（[二维码](https://channels.weixin.qq.com/login.html)） |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | String |  |

## 模块：`shou-cang-jia`

### POST /weChatFavorites/delFavItem

- operationId: `shou_cang_jia_shan_chu_shou_cang_jia_nei_rong`
- title: 删除收藏夹内容
- doc: `docs/api/api-wen-dang2/shou-cang-jia/shan-chu-shou-cang-jia-nei-rong.md`
- requestUrl (as documented): `http://域名地址/weChatFavorites/delFavItem`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 微信实列ID |
| favId | 是 | int | 收藏标识 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |

### POST /weChatFavorites/favSync

- operationId: `shou_cang_jia_huo_qu_shou_cang_jia_lie_biao`
- title: 获取收藏夹列表
- doc: `docs/api/api-wen-dang2/shou-cang-jia/huo-qu-shou-cang-jia-lie-biao.md`
- requestUrl (as documented): `http://域名地址/weChatFavorites/favSync`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 微信实列ID |
| keyBuf | 是 | byte\[\] | 第一次传null,如果接口返回keyBuf第二次传keyBuf |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| ret | int | 接口状态 0:成功 |
| favList | list | 收藏列表 |
| keyBuf | byte\[\] | 同步密钥 |
| continueFlag | int | 0:表示同步结束，1:表示还需要继续同步 |
| favId | int | 收藏标识 |
| type | int | 收藏类型 |
| updateTime | long | 收藏时间戳 |

### POST /weChatFavorites/getFavItem

- operationId: `shou_cang_jia_huo_qu_shou_cang_jia_nei_rong`
- title: 获取收藏夹内容
- doc: `docs/api/api-wen-dang2/shou-cang-jia/huo-qu-shou-cang-jia-nei-rong.md`
- requestUrl (as documented): `http://域名地址/weChatFavorites/getFavItem`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | String | 微信实列ID |
| favId | 是 | int | 收藏标识 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| object | xml | 收藏详情 |
| updateTime | long | 收藏时间戳 |

## 模块：`te-shu`

### POST /cdnDownFile

- operationId: `te_shu_cdnDownFile`
- title: CDN资源下载
- doc: `docs/api/api-wen-dang2/te-shu/cdnDownFile.md`
- requestUrl (as documented): `http://域名地址/cdnDownFile`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| cdnUrl | 是 | string | XML获取 |
| aeskey | 是 | string | XML获取 |
| fileType | 是 | int |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |

### POST /getReqTimes

- operationId: `te_shu_getReqTimes`
- title: 查询接口调用次数
- doc: `docs/api/api-wen-dang2/te-shu/getReqTimes.md`
- requestUrl (as documented): `http://域名地址/getReqTimes`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| account | string | 开发者账号 |
| nickName | string | 微信昵称 |
| wcId | string | 微信id |
| times | string | 接口调用次数 |
| wid | string | 登录实例标识 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| account | string | 开发者账号 |
| nickName | string | 微信昵称 |
| wcId | string | 微信id |
| times | string | 接口调用次数 |
| wid | string | 登录实例标识 |

### POST /getUserFlow

- operationId: `te_shu_getUserFlow`
- title: 查询使用流量
- doc: `docs/api/api-wen-dang2/te-shu/getUserFlow.md`
- requestUrl (as documented): `http://域名地址/getUserFlow`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| account | string | 开发者账号 |
| nickName | string | 微信昵称 |
| wcId | string | 微信id |
| flow | string | 使用流量 |
| size | int | 使用流量（以B为单位） |
| wid | string | 登录实例标识 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| account | string | 开发者账号 |
| nickName | string | 微信昵称 |
| wcId | string | 微信id |
| flow | string | 使用流量 |
| size | int | 使用流量（以B为单位） |
| wid | string | 登录实例标识 |

### POST /offlineReason

- operationId: `te_shu_offlineReason`
- title: 查询掉线原因
- doc: `docs/api/api-wen-dang2/te-shu/offlineReason.md`
- requestUrl (as documented): `http://域名地址/offlineReason`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wcId | 是 | string | 微信id |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| wcId | string | 微信id |
| reason | string | 掉线原因（null则是在线） |

### POST /sendCdnVideo

- operationId: `te_shu_sendCdnVideo`
- title: CDN视频上传
- doc: `docs/api/api-wen-dang2/te-shu/sendCdnVideo.md`
- requestUrl (as documented): `http://域名地址/sendCdnVideo`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回 **参数：**

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| path | 是 | string | 视频url链接 |
| thumbPath | 是 | string | 图片url链接 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| cdnUrl | string | 视频cdn信息 |
| aesKey | string | 视频key信息 |
| length | string | 视频长度 |

### POST /setproxy

- operationId: `te_shu_setproxy`
- title: 动态设置代理IP
- doc: `docs/api/api-wen-dang2/te-shu/setproxy.md`
- requestUrl (as documented): `http://域名地址/setproxy`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wcId | 是 | string | 微信id |
| proxyIp | 是 | string | 代理IP+端口 |
| proxyUser | 是 | string | 代理IP平台账号 |
| proxyPassword | 是 | string | 代理IP平台密码 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |

### POST /uploadCdnImage

- operationId: `te_shu_uploadCdnImage`
- title: CDN图片上传
- doc: `docs/api/api-wen-dang2/te-shu/uploadCdnImage.md`
- requestUrl (as documented): `http://域名地址/uploadCdnImage`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回 **参数：**

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| content | 是 | string | 图片url链接 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| cdnUrl | string | 图片cdn信息（用于自定义小程序图片参数） |
| aesKey | string | 图片key信息（用于自定义小程序图片参数） |
| hdLength | string | 图片大小（用于自定义小程序图片参数） |

## 模块：`wei-xin-guan-li`

### POST /isOnline

- operationId: `wei_xin_guan_li_cha_xun_wei_xin_shi_fou_zai_xian`
- title: 查询微信是否在线
- doc: `docs/api/api-wen-dang2/wei-xin-guan-li/cha-xun-wei-xin-shi-fou-zai-xian.md`
- requestUrl (as documented): `http://域名地址/isOnline`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功（在线），1001失败（离线） |
| msg | string | 反馈信息 |

### POST /member/offline

- operationId: `wei_xin_guan_li_pi_liang_xia_xian_wei_xin_hao`
- title: 批量下线微信号
- doc: `docs/api/api-wen-dang2/wei-xin-guan-li/pi-liang-xia-xian-wei-xin-hao.md`
- requestUrl (as documented): `http://域名地址/member/offline`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| account | 是 | string | 账号 |
| wcIds | 是 | list | 须下线的微信id |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |

### POST /queryLoginWx

- operationId: `wei_xin_guan_li_duan_xian_chong_lian`
- title: 查询账号中在线的微信列表
- doc: `docs/api/api-wen-dang2/wei-xin-guan-li/duan-xian-chong-lian.md`
- requestUrl (as documented): `http://域名地址/queryLoginWx`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功（在线），1001失败（离线） |
| message | string | 反馈信息 |
| wcId | string | 微信id |
| wId | string | 登录实例标识 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功（在线），1001失败（离线） |
| message | string | 反馈信息 |
| wcId | string | 微信id |
| wId | string | 登录实例标识 |

## 模块：`xiao-xi-fa-song`

### POST /forwardUrl

- operationId: `xiao_xi_fa_song_forwardUrl`
- title: 转发链接消息
- doc: `docs/api/api-wen-dang2/xiao-xi-fa-song/forwardUrl.md`
- requestUrl (as documented): `http://域名地址/forwardUrl`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 接收人微信id/群id |
| content | 是 | string | xml文件内容 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| data.type | int | 类型 |
| data.msgId | long | 消息msgId |
| data.newMsgId | long | 消息newMsgId |
| data.createTime | long | 消息发送时间戳 |
| data.wcId | string | 消息接收方id |

### POST /revokeMsg

- operationId: `xiao_xi_fa_song_revokeMsg`
- title: 撤回消息
- doc: `docs/api/api-wen-dang2/xiao-xi-fa-song/revokeMsg.md`
- requestUrl (as documented): `http://域名地址/revokeMsg`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 接收方微信id/群id |
| msgId | 是 | long | 消息msgId(发送类接口返回的msgId) |
| newMsgId | 是 | long | 消息newMsgId(发送类接口返回的newMsgId) |
| createTime | 是 | long | 发送时间 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |

### POST /sendApplet

- operationId: `xiao_xi_fa_song_sendApp`
- title: 发送APP类消息
- doc: `docs/api/api-wen-dang2/xiao-xi-fa-song/sendApp.md`
- requestUrl (as documented): `http://域名地址/sendApplet`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 接收方微信id/群id |
| content | 是 | string | 消息xml回调内容, (此回调的XML需要去掉部分，截取appmsg开头的，具体请看请求参数示例） |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| data.type | int | 类型 |
| data.msgId | long | 消息msgId |
| data.newMsgId | long | 消息newMsgId |
| data.createTime | long | 消息发送时间戳 |
| data.wcId | string | 消息接收方id |

### POST /sendApplet

- operationId: `xiao_xi_fa_song_sendApplet`
- title: 转发小程序
- doc: `docs/api/api-wen-dang2/xiao-xi-fa-song/sendApplet.md`
- requestUrl (as documented): `http://域名地址/sendApplet`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 接收方微信id/群id |
| imgUrl | 是 | string |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| data.type | int | 类型 |
| data.msgId | long | 消息msgId |
| data.newMsgId | long | 消息newMsgId |
| data.createTime | long | 消息发送时间戳 |
| data.wcId | string | 消息接收方id |

### POST /sendApplets

- operationId: `xiao_xi_fa_song_sendApplets`
- title: 发送小程序
- doc: `docs/api/api-wen-dang2/xiao-xi-fa-song/sendApplets.md`
- requestUrl (as documented): `http://域名地址/sendApplets`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 接收方微信id/群id |
| displayName | 是 | string | 小程序的名称，例如：京东 |
| iconUrl | 是 | string |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| data.type | int | 类型 |
| data.msgId | long | 消息msgId |
| data.newMsgId | long | 消息newMsgId |
| data.createTime | long | 消息发送时间戳 |
| data.wcId | string | 消息接收方id |

### POST /sendEmoji

- operationId: `xiao_xi_fa_song_fa_song_emoji`
- title: 发送emoji表情
- doc: `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-emoji.md`
- requestUrl (as documented): `http://域名地址/sendEmoji`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 接收人微信id/群id |
| imageMd5 | 是 | string | 取回调中xml中md5字段值 |
| imgSize | 是 | string | 取回调中xml中len字段值 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| data.type | int | 类型 |
| data.msgId | long | 消息msgId |
| data.newMsgId | long | 消息newMsgId |
| data.createTime | long | 消息发送时间戳 |
| data.wcId | string | 消息接收方id |

### POST /sendFile

- operationId: `xiao_xi_fa_song_sendFile`
- title: 发送文件
- doc: `docs/api/api-wen-dang2/xiao-xi-fa-song/sendFile.md`
- requestUrl (as documented): `http://域名地址/sendFile`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 接收方微信id/群id |
| path | 是 | string | 文件url链接 |
| fileName | 是 | string | 文件名 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| data.type | int | 类型 |
| data.msgId | long | 消息msgId |
| data.newMsgId | long | 消息newMsgId |
| data.createTime | long | 消息发送时间戳 |
| data.wcId | string | 消息接收方id |

### POST /sendFileBase64

- operationId: `xiao_xi_fa_song_sendFileBase64`
- title: 发送文件
- doc: `docs/api/api-wen-dang2/xiao-xi-fa-song/sendFileBase64.md`
- requestUrl (as documented): `http://域名地址/sendFileBase64`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 接收方微信id/群id |
| fileName | 是 | string | 文件名 |
| base64 | 是 | string |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| data.type | int | 类型 |
| data.msgId | long | 消息msgId |
| data.newMsgId | long | 消息newMsgId |
| data.createTime | long | 消息发送时间戳 |
| data.wcId | string | 消息接收方id |

### POST /sendImage2

- operationId: `xiao_xi_fa_song_fa_song_tu_pian_xiao_xi2`
- title: 发送图片消息
- doc: `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-tu-pian-xiao-xi2.md`
- requestUrl (as documented): `http://域名地址/sendImage2`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回 **参数：**

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 接收人微信id/群id |
| content | 是 | string | 图片url链接 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| data.type | int | 类型 |
| data.msgId | long | 消息msgId |
| data.newMsgId | long | 消息newMsgId |
| data.createTime | long | 消息发送时间戳 |
| data.wcId | string | 消息接收方id |

### POST /sendNameCard

- operationId: `xiao_xi_fa_song_fa_song_ming_pian_xiao_xi`
- title: 发送名片消息
- doc: `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-ming-pian-xiao-xi.md`
- requestUrl (as documented): `http://域名地址/sendNameCard`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 接收人微信id/群id |
| nameCardId | 是 | string | 要发送的名片微信id |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| data.type | int | 类型 |
| data.msgId | long | 消息msgId |
| data.newMsgId | long | 消息newMsgId |
| data.createTime | long | 消息发送时间戳 |
| data.wcId | string | 消息接收方id |

### POST /sendRecvFile

- operationId: `xiao_xi_fa_song_fa_song_yi_jing_shou_dao_de_wen_jian`
- title: 转发文件消息
- doc: `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-yi-jing-shou-dao-de-wen-jian.md`
- requestUrl (as documented): `http://域名地址/sendRecvFile`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 接收人微信id/群id |
| content | 是 | string | xml文件内容 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| data.type | int | 类型 |
| data.msgId | long | 消息msgId |
| data.newMsgId | long | 消息newMsgId |
| data.createTime | long | 消息发送时间戳 |
| data.wcId | string | 消息接收方id |

### POST /sendRecvImage

- operationId: `xiao_xi_fa_song_fa_song_yi_jing_shou_dao_de_tu_pian_xiao_xi`
- title: 转发图片消息
- doc: `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-yi-jing-shou-dao-de-tu-pian-xiao-xi.md`
- requestUrl (as documented): `http://域名地址/sendRecvImage`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回 **参数：**

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 接收人微信id/群id |
| content | 是 | string | xml图片内容 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| data.type | int | 类型 |
| data.msgId | long | 消息msgId |
| data.newMsgId | long | 消息newMsgId |
| data.createTime | long | 消息发送时间戳 |
| data.wcId | string | 消息接收方id |

### POST /sendRecvVideo

- operationId: `xiao_xi_fa_song_fa_song_yi_jing_shou_dao_de_shi_pin_xiao_xi`
- title: 转发视频消息
- doc: `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-yi-jing-shou-dao-de-shi-pin-xiao-xi.md`
- requestUrl (as documented): `http://域名地址/sendRecvVideo`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 接收人微信id/群号id |
| content | 是 | string | xml视频内容 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| data.type | int | 类型 |
| data.msgId | long | 消息msgId |
| data.newMsgId | long | 消息newMsgId |
| data.createTime | long | 消息发送时间戳 |
| data.wcId | string | 消息接收方id |

### POST /sendText

- operationId: `xiao_xi_fa_song_fa_song_wen_ben_xiao_xi`
- title: 发送文本消息
- doc: `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-wen-ben-xiao-xi.md`
- requestUrl (as documented): `http://域名地址/sendText`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 接收人微信id/群id |
| content | 是 | string | 文本内容消息 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| data.type | int | 类型 |
| data.msgId | long | 消息msgId |
| data.newMsgId | long | 消息newMsgId |
| data.createTime | long | 消息发送时间戳 |
| data.wcId | string | 消息接收方id |

### POST /sendText

- operationId: `xiao_xi_fa_song_qun_liao_at`
- title: 群聊@
- doc: `docs/api/api-wen-dang2/xiao-xi-fa-song/qun-liao-at.md`
- requestUrl (as documented): `http://域名地址/sendText`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 接收方群id |
| content | 是 | string | 文本内容消息（@的微信昵称需要自己拼接，必须拼接艾特符号，不然不生效） |
| at | 是 | string |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| data.type | int | 类型 |
| data.msgId | long | 消息msgId |
| data.newMsgId | long | 消息newMsgId |
| data.createTime | long | 消息发送时间戳 |
| data.wcId | string | 消息接收方id |

### POST /sendUrl

- operationId: `xiao_xi_fa_song_fa_song_lian_jie_xiao_xi`
- title: 发送链接
- doc: `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-lian-jie-xiao-xi.md`
- requestUrl (as documented): `http://域名地址/sendUrl`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 接收人微信id/群id |
| title | 是 | string | 标题 |
| url | 是 | string | 链接 |
| description | 是 | string | 描述 |
| thumbUrl | 是 | string | 图标url（JPG/PNG格式,50K以内） |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| data.type | int | 类型 |
| data.msgId | long | 消息msgId |
| data.newMsgId | long | 消息newMsgId |
| data.createTime | long | 消息发送时间戳 |
| data.wcId | string | 消息接收方id |

### POST /sendVideo

- operationId: `xiao_xi_fa_song_fa_song_shi_pin_xiao_xi`
- title: 发送视频消息
- doc: `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-shi-pin-xiao-xi.md`
- requestUrl (as documented): `http://域名地址/sendVideo`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 接收人微信id/群id |
| path | 是 | string | 视频url链接 |
| thumbPath | 是 | string | 视频封面url链接（50KB以内） |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| data.type | int | 类型 |
| data.msgId | long | 消息msgId |
| data.newMsgId | long | 消息newMsgId |
| data.createTime | long | 消息发送时间戳 |
| data.wcId | string | 消息接收方id |

### POST /sendVoice

- operationId: `xiao_xi_fa_song_fa_song_yu_yin_xiao_xi_ji_jiang_kai_fang`
- title: 发送语音
- doc: `docs/api/api-wen-dang2/xiao-xi-fa-song/fa-song-yu-yin-xiao-xi-ji-jiang-kai-fang.md`
- requestUrl (as documented): `http://域名地址/sendVoice`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| wcId | 是 | string | 接收人微信id/群id |
| content | 是 | string | 语音url （silk/amr 格式,可以[下载消息中的语音返回silk格式](../xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/xia-zai-yu-yin-ji-jiang-kai-fang.html)） |
| length | 是 | int | 语音时长（回调消息xml数据中的voicelength字段） |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data |  |  |
| data.type | int | 类型 |
| data.msgId | long | 消息msgId |
| data.newMsgId | long | 消息newMsgId |
| data.createTime | long | 消息发送时间戳 |
| data.wcId | string | 消息接收方id |

## 模块：`xiao-xi-jie-shou`

### POST /asynGetMsgVideo

- operationId: `xiao_xi_jie_shou_asynGetMsgVideo`
- title: 异步下载消息中的视频
- doc: `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/asynGetMsgVideo.md`
- requestUrl (as documented): `http://域名地址/asynGetMsgVideo`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 (包含此参数 所有参数都是从消息回调中取） |
| msgId | 是 | long | 消息id |
| content | 是 | string | 收到的消息的xml数据 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data | string |  |
| data.id | string | 异步下载视频id，可用此参数[获取下载视频结果](getMsgVideoRes.html) |

### POST /cancelHttpCallbackUrl

- operationId: `xiao_xi_jie_shou_qu_xiao_xiao_xi_jie_shou`
- title: 取消消息接收
- doc: `docs/api/api-wen-dang2/xiao-xi-jie-shou/shou-xiao-xi/qu-xiao-xiao-xi-jie-shou.md`
- requestUrl (as documented): `http://域名地址/cancelHttpCallbackUrl`

**Headers（文档提取）**
- Authorization: login接口返回
- Content-Type: application/json

**参数（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |

### POST /getMsgEmoji

- operationId: `xiao_xi_jie_shou_getMsgEmoji`
- title: 下载消息中的动图
- doc: `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/getMsgEmoji.md`
- requestUrl (as documented): `http://域名/getMsgEmoji`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 |
| msgId | 是 | int | 消息回调中返回 |
| content | 是 | string | 消息回调中返回，收到的emoji消息的xml数据 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| url | string | url地址 |

### POST /getMsgFile

- operationId: `xiao_xi_jie_shou_xia_zai_wen_jian_ji_jiang_kai_fang`
- title: 下载文件
- doc: `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/xia-zai-wen-jian-ji-jiang-kai-fang.md`
- requestUrl (as documented): `http://域名地址/getMsgFile`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 包含此参数 所有参数都是从消息回调中取） |
| msgId | 是 | long | 消息id |
| content | 是 | string | 收到的消息的xml数据 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |

### POST /getMsgImg

- operationId: `xiao_xi_jie_shou_xia_zai_tu_pian_ji_jiang_kai_fang`
- title: 下载图片
- doc: `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/xia-zai-tu-pian-ji-jiang-kai-fang.md`
- requestUrl (as documented): `http://域名地址/getMsgImg`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 (包含此参数 所有参数都是从消息回调中取） |
| msgId | 是 | long | 消息id |
| content | 是 | string | 收到的消息的xml数据 |
| type | 否 | int |  |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| url | string | 图片地址（7日内有效） |

### POST /getMsgVideoRes

- operationId: `xiao_xi_jie_shou_getMsgVideoRes`
- title: 获取异步下载视频消息结果
- doc: `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/getMsgVideoRes.md`
- requestUrl (as documented): `http://域名地址/getMsgVideoRes`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| id | 是 | string | [异步下载视频接口](asynGetMsgVideo.html)返回的id |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |
| data | string | 下载结果 |

### POST /getMsgVoice

- operationId: `xiao_xi_jie_shou_xia_zai_yu_yin_ji_jiang_kai_fang`
- title: 下载消息中的语音
- doc: `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/xia-zai-yu-yin-ji-jiang-kai-fang.md`
- requestUrl (as documented): `http://域名地址/getMsgVoice`

**Headers（文档提取）**
- Content-Type: application/json
- Authorization: login接口返回

**参数（文档提取）**

| 参数名 | 必选 | 类型 | 说明 |
| --- | --- | --- | --- |
| wId | 是 | string | 登录实例标识 包含此参数 所有参数都是从消息回调中取） |
| msgId | 是 | long | 消息id |
| length | 是 | int | 语音长度（xml数据中的length字段） |
| bufId | 是 | string | xml中返回的bufId字段值 |
| fromUser | 是 | string | 发送者 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |

### POST /setHttpCallbackUrl

- operationId: `xiao_xi_jie_shou_she_zhi_http_hui_tiao_di_zhi`
- title: 设置消息接收地址
- doc: `docs/api/api-wen-dang2/xiao-xi-jie-shou/shou-xiao-xi/she-zhi-http-hui-tiao-di-zhi.md`
- requestUrl (as documented): `http://域名地址/setHttpCallbackUrl`

**Headers（文档提取）**
- Content-Type: application/json
- **Authorization: login接口返回**

**参数（文档提取）**

| 参数名 | 必填 | 类型 | 说明 |
| --- | --- | --- | --- |
| httpUrl | 是 | string | 开发者接口回调地址 |
| type | 是 | int | 2:[优化版](callback.html)【PS：建议使用优化版】 |

**返回数据（文档提取）**

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| code | string | 1000成功，1001失败 |
| msg | string | 反馈信息 |

## Reference Docs（非 endpoint）

| title | doc |
|---|---|
| 回调消息内容释义-优化版 | `docs/api/api-wen-dang2/xiao-xi-jie-shou/shou-xiao-xi/callback.md` |

## Category Docs（目录页）

| title | doc |
|---|---|
| 标签 | `docs/api/api-wen-dang2/biao-qian/README.md` |
| 好友操作 | `docs/api/api-wen-dang2/deng-lu/README.md` |
| 好友操作 | `docs/api/api-wen-dang2/hao-you-cao-zuo/README.md` |
| 朋友圈 | `docs/api/api-wen-dang2/peng-you-quan/README.md` |
| 群操作 | `docs/api/api-wen-dang2/qun-cao-zuo/README.md` |
| API 文档 | `docs/api/api-wen-dang2/README.md` |
| 视频号 | `docs/api/api-wen-dang2/shipinhao/README.md` |
| 收藏夹 | `docs/api/api-wen-dang2/shou-cang-jia/README.md` |
| 工具箱 | `docs/api/api-wen-dang2/te-shu/README.md` |
| 账户管理 | `docs/api/api-wen-dang2/wei-xin-guan-li/README.md` |
| 消息发送 | `docs/api/api-wen-dang2/xiao-xi-fa-song/README.md` |
| 消息接收 | `docs/api/api-wen-dang2/xiao-xi-jie-shou/README.md` |
| 消息回调配置 | `docs/api/api-wen-dang2/xiao-xi-jie-shou/shou-xiao-xi/README.md` |
| 下载消息内容 | `docs/api/api-wen-dang2/xiao-xi-jie-shou/xia-zai-xiao-xi-nei-rong/README.md` |
