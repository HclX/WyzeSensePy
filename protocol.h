enum
{
    PACKET_TYPE_SYNC    = 0x43,
    PACKET_TYPE_ASYNC   = 0x53,
};

enum
{
    // single byte result (0x01) in response
    H2D_SYNC_INQUIRY  = 0x27,

    // 16-byte random in pyaload, 16-byte result in response 
    H2D_SYNC_GET_ENR  = 0x02,
    
    // 8-byte ASCII string MAC address in response
    H2D_SYNC_GET_MAC = 0X04,

    // 16-byte ASCII string key 
    H2D_SYNC_GET_KEY = 0X06,

    // single byte result, number of bond snesors
    H2D_ASYNC_GET_SENSOR_COUNT  = 0x2E,

    // single byte number of sensors in payload, multiple response, with sensor mac in payload
    H2D_ASYNC_GET_SENSOR_LIST = 0x30,

    // single byte payload, 0x01 for start, 0x00 for stop
    H2D_ASYNC_START_NETWORK = 0x1C,

    // single byte payload (0xFF)
    H2D_ASYNC_AUTH_DONE = 0X14,

    // <event> in payload
    H2D_ASYNC_DEL_SENSOR = 0X25,

    // variable length version result in response, ex: "version[0.0.0.30][V1.4][Dongle][UD3U]"
    H2D_ASYNC_GET_VER = 0X16,

    // 16-byte random, response struct sensor info
    H2D_ASYNC_SET_SENSOR_RANDOM = 0x21,

    // variable length event struct, no need to response.
    D2H_ASYNC_LOG_EVENT = 0x35,
};

struct dongle_pkt_t
{
    // '\x55\xAA' or '\xAA\x55', depending on the data flow direction
    uint8_t magic[2];
    // 0x43 or 0x53
    uint8_t type;
    // length of the payload
    uint8_t length;
    // command
    uint8_t cmd;
    // variable length payload. last two bytes of the payload is the
    // checksum by adding all the previous bytes together.
    uint8_t payload[0]; 
};

struct dongle_event_hdr_t
{
    uint64_t timestamp;
    uint8_t payload_size;
    uint8_t payload[0];
};


enum 
{
    EVENT_TYPE_NETWORK_STATUS = H2D_ASYNC_START_NETWORK,
    EVENT_TYPE_SENSOR_SCAN = 0xA3,
    EVENT_TYPE_SENSOR_ALARM = 0xA2,
};

enum
{
    SENSOR_TYPE_DWS3U = 1,
    SENSOR_TYPE_PIR3U = 2,
};

struct dongle_network_event_t
{
    uint8_t status;
};

struct dongle_sensor_scan_event_t
{
    uint8_t mac[8];
    uint8_t type;
    uint8_t version;
};

[DONGLE_RECORD->dongle.c,2071]:====================recevied from dongle==================
[DONGLE_RECORD->dongle.c,2072]:[55][aa][53][1d][19][00][00][01][6a][c4][11][6f][9f][a2][37][37][37][43][44][36][34][37][01][14][5a][00][01][01][00][01][34][06][eb]
[DONGLE_RECORD->dongle.c,2817]:====================write to dongle==================
[DONGLE_RECORD->dongle.c,2818]:[aa][55][53][19][ff][02][6a]
[DONGLE_RECORD->dongle.c,137]:DONGLE SEND ACK
[DONGLE_RECORD->dongle.c,1685]:dongle alarm sensor_id:[777CD647], camera_time[1558067648130],dongle_time[1558067638175]!!
[DONGLE_RECORD->dongle.c,2071]:====================recevied from dongle==================
[DONGLE_RECORD->dongle.c,2072]:[55][aa][53][1d][19][00][00][01][6a][c4][11][70][13][a1][37][37][37][43][44][36][34][37][01][14][5c][00][01][01][00][01][36][06][63]
[DONGLE_RECORD->dongle.c,2817]:====================write to dongle==================
[DONGLE_RECORD->dongle.c,2818]:[aa][55][53][19][ff][02][6a]
[DONGLE_RECORD->dongle.c,137]:DONGLE SEND ACK
msg_queue_rcv time: 5CDE39C0, id: 98307, type: 1500, cmd: 1508
[IOT] msgsend {"mac":"A4DA222B22C4","model":"WYZECAM1","sub_mac":"777CD647","sub_model":"DWS3U","data":{"P1301":"1","P1303":"90","P1304":"52","P1329":"0"},"ts":1558067638175} success!
msg_queue_rcv time: 5CDE39C1, id: 98307, type: 1500, cmd: 1508
[IOT] msgsend {"mac":"A4DA222B22C4","model":"WYZECAM1","sub_mac":"777CD647","sub_model":"DWS3U","data":{"P1303":"92","P1304":"54","P1329":"0"},"ts":1558067648257} success!


[DONGLE_RECORD->dongle.c,2072]:[55][aa][53][1d][19][00][00][01][6a][c4][11][7e][3f][a2][37][37][37][43][44][36][34][37][01][14][5c][00][01][00][00][02][3d][06][a5]
[DONGLE_RECORD->dongle.c,2817]:====================write to dongle==================
[DONGLE_RECORD->dongle.c,2818]:[aa][55][53][19][ff][02][6a]
[DONGLE_RECORD->dongle.c,137]:DONGLE SEND ACK
[DONGLE_RECORD->dongle.c,1685]:dongle alarm sensor_id:[777CD647], camera_time[1558067652067],dongle_time[1558067641919]!!
msg_queue_rcv time: 5CDE39C4, id: 98307, type: 1500, cmd: 1508
[IOT] msgsend {"mac":"A4DA222B22C4","model":"WYZECAM1","sub_mac":"777CD647","sub_model":"DWS3U","data":{"P1301":"0","P1303":"92","P1304":"61","P1329":"0"},"ts":1558067641919} success!


[DONGLE_RECORD->dongle.c,2071]:====================recevied from dongle==================
[DONGLE_RECORD->dongle.c,2072]:[55][aa][53][1d][19][00][00][01][6a][c4][12][5b][75][a2][37][37][37][43][43][34][35][31][01][15][57][00][01][01][00][01][30][06][a0]
[DONGLE_RECORD->dongle.c,2817]:====================write to dongle==================
[DONGLE_RECORD->dongle.c,2818]:[aa][55][53][19][ff][02][6a]
[DONGLE_RECORD->dongle.c,137]:DONGLE SEND ACK
[DONGLE_RECORD->dongle.c,1685]:dongle alarm sensor_id:[777CC451], camera_time[1558067711589],dongle_time[1558067698549]!!
[DONGLE_RECORD->dongle.c,2071]:====================recevied from dongle==================
[DONGLE_RECORD->dongle.c,2072]:[55][aa][53][1d][19][00][00][01][6a][c4][12][5b][e6][a1][37][37][37][43][43][34][35][31][01][15][59][00][01][01][00][01][30][07][12]
[DONGLE_RECORD->dongle.c,2817]:====================write to dongle==================
[DONGLE_RECORD->dongle.c,2818]:[aa][55][53][19][ff][02][6a]
[DONGLE_RECORD->dongle.c,137]:DONGLE SEND ACK
msg_queue_rcv time: 5CDE3A00, id: 98307, type: 1500, cmd: 1508
[IOT] msgsend {"mac":"A4DA222B22C4","model":"WYZECAM1","sub_mac":"777CC451","sub_model":"DWS3U","data":{"P1301":"1","P1303":"87","P1304":"48","P1329":"0"},"ts":1558067698549} success!

msg_queue_rcv time: 5CDE3A01, id: 98307, type: 1500, cmd: 1508
[IOT] msgsend {"mac":"A4DA222B22C4","model":"WYZECAM1","sub_mac":"777CC451","sub_model":"DWS3U","data":{            "P1303":"89","P1304":"48","P1329":"0"},"ts":1558067711718} success!


[DONGLE_RECORD->dongle.c,2071]:====================recevied from dongle==================
[DONGLE_RECORD->dongle.c,2072]:[55][aa][53][1d][19][00][00][01][6a][c4][12][64][19][a2][37][37][37][43][43][34][35][31][01][17][59][00][01][00][00][02][28][06][49]
[DONGLE_RECORD->dongle.c,2817]:====================write to dongle==================
[DONGLE_RECORD->dongle.c,2818]:[aa][55][53][19][ff][02][6a]
[DONGLE_RECORD->dongle.c,137]:DONGLE SEND ACK
[DONGLE_RECORD->dongle.c,1685]:dongle alarm sensor_id:[777CC451], camera_time[1558067713915],dongle_time[1558067700761]!!
msg_queue_rcv time: 5CDE3A02, id: 98307, type: 1500, cmd: 1508
[IOT] msgsend {"mac":"A4DA222B22C4","model":"WYZECAM1","sub_mac":"777CC451","sub_model":"DWS3U","data":{"P1301":"0","P1303":"89","P1304":"40","P1329":"0"},"ts":1558067700761} success!


[DONGLE_RECORD->dongle.c,2071]:====================recevied from dongle==================
[DONGLE_RECORD->dongle.c,2072]:[55][aa][53][1d][19][00][00][01][6a][c4][12][6d][55][a2][37][37][37][43][43][34][35][31][01][17][61][00][01][01][00][03][30][06][a0]
[DONGLE_RECORD->dongle.c,2817]:====================write to dongle==================
[DONGLE_RECORD->dongle.c,2818]:[aa][55][53][19][ff][02][6a]
[DONGLE_RECORD->dongle.c,137]:DONGLE SEND ACK
[DONGLE_RECORD->dongle.c,1685]:dongle alarm sensor_id:[777CC451], camera_time[1558067716401],dongle_time[1558067703125]!!


[DONGLE_RECORD->dongle.c,2071]:====================recevied from dongle==================
[DONGLE_RECORD->dongle.c,2072]:[55][aa][53][1d][19][00][00][01][6a][c4][12][6f][99][a2][37][37][37][43][43][34][35][31][01][17][61][00][01][00][00][04][2b][06][e1]
[DONGLE_RECORD->dongle.c,2817]:====================write to dongle==================
[DONGLE_RECORD->dongle.c,2818]:[aa][55][53][19][ff][02][6a]
[DONGLE_RECORD->dongle.c,137]:DONGLE SEND ACK
[DONGLE_RECORD->dongle.c,1685]:dongle alarm sensor_id:[777CC451], camera_time[1558067717008],dongle_time[1558067703705]!!
msg_queue_rcv time: 5CDE3A05, id: 98307, type: 1500, cmd: 1508
[IOT] msgsend {"mac":"A4DA222B22C4","model":"WYZECAM1","sub_mac":"777CC451","sub_model":"DWS3U","data":{"P1301":"1","P1303":"97","P1304":"48","P1329":"0"},"ts":1558067703125} success!


[DONGLE_RECORD->dongle.c,2071]:====================recevied from dongle==================
[DONGLE_RECORD->dongle.c,2072]:[55][aa][53][1d][19][00][00][01][6a][c4][12][73][46][a2][37][37][37][43][43][34][35][31][01][17][61][00][01][01][00][05][30][06][99]
[DONGLE_RECORD->dongle.c,2817]:====================write to dongle==================
[DONGLE_RECORD->dongle.c,2818]:[aa][55][53][19][ff][02][6a]
[DONGLE_RECORD->dongle.c,137]:DONGLE SEND ACK
[DONGLE_RECORD->dongle.c,1685]:dongle alarm sensor_id:[777CC451], camera_time[1558067717998],dongle_time[1558067704646]!!
msg_queue_rcv time: 5CDE3A06, id: 98307, type: 1500, cmd: 1508
[IOT] msgsend {"mac":"A4DA222B22C4","model":"WYZECAM1","sub_mac":"777CC451","sub_model":"DWS3U","data":{"P1301":"0","P1303":"97","P1304":"43","P1329":"0"},"ts":1558067703705} success!


[DONGLE_RECORD->dongle.c,2071]:====================recevied from dongle==================
[DONGLE_RECORD->dongle.c,2072]:[55][aa][53][1d][19][00][00][01][6a][c4][12][75][fc][a2][37][37][37][43][43][34][35][31][01][17][61][00][01][00][00][06][31][07][52]
[DONGLE_RECORD->dongle.c,2817]:====================write to dongle==================
[DONGLE_RECORD->dongle.c,2818]:[aa][55][53][19][ff][02][6a]
[DONGLE_RECORD->dongle.c,137]:DONGLE SEND ACK
[DONGLE_RECORD->dongle.c,1685]:dongle alarm sensor_id:[777CC451], camera_time[1558067718734],dongle_time[1558067705340]!!
msg_queue_rcv time: 5CDE3A07, id: 98307, type: 1500, cmd: 1508
[IOT] msgsend {"mac":"A4DA222B22C4","model":"WYZECAM1","sub_mac":"777CC451","sub_model":"DWS3U","data":{"P1301":"1","P1303":"97","P1304":"48","P1329":"0"},"ts":1558067704646} success!
msg_queue_rcv time: 5CDE3A08, id: 98307, type: 1500, cmd: 1508
[IOT] msgsend {"mac":"A4DA222B22C4","model":"WYZECAM1","sub_mac":"777CC451","sub_model":"DWS3U","data":{"P1301":"0","P1303":"97","P1304":"49","P1329":"0"},"ts":1558067705340} success!

struct dongle_sensor_alarm_event_t
{
    uint8_t mac[8];

}
//[DONGLE_RECORD->dongle.c,2072]:[55][aa][53][1e][22][a5][37][37][37][43][44][36][34][37][3c][64][bf][e0][b9][cd][11][0a][f4][9d][b0][14][ee][17][78][eb][01][10][0c][b2]
//[DONGLE_RECORD->dongle.c,2072]:[55][aa][53][1e][22][a5][37][37][37][43][31][46][43][41][61][b1][ca][4c][41][3a][26][b5][55][c7][d6][1a][4e][a7][ad][14][02][19][0b][75]
//[DONGLE_RECORD->dongle.c,2072]:[55][aa][53][1e][22][a5][37][37][37][43][43][34][35][31][f9][45][54][d8][12][43][69][c4][1b][c8][27][e6][ce][99][a7][32][01][10][0c][29]

struct dongle_sensor_info_t
{
    uint8_t something; // 0xA5
    uint8_t mac[8];
    uint8_t R1[16];
    uint8_t type;
    uint8_t version;
}