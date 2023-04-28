// 让js读 src 文件夹下的settings.json文件
// const fs = require('fs');
// const path = require('path');
// const settings = require('./settings.json');


// 默认初始地图位置: 中铁建洋湖一品
const defaultLocation = [112.909374, 28.126375];
const defaultZoom = 19;
const defaultQuantity = 2;
const mercator = 20037508.34 / 180;
const defaultZooms = [2, 20]
const defaultRotation = -15

// 记录当前 坐标 
var currlat = defaultLocation[1];
var currlng = defaultLocation[0];

// 创建新地图
var map = new AMap.Map('container', {
    rotateEnable: true,
    pitchEnable: true,
    pitch: 50,
    rotation: defaultRotation,
    viewMode: '3D', //开启3D视图,默认为关闭
    center: defaultLocation,
    zooms: defaultZooms,
    zoom: defaultZoom,
    features: ['bg', 'road', 'building', 'point']
});

var autoOptions = {
    input: "search"
};

AMap.plugin(['AMap.PlaceSearch', 'AMap.AutoComplete'], function () {
    var auto = new AMap.AutoComplete(autoOptions);
    var placeSearch = new AMap.PlaceSearch({
        map: map
    }); //构造地点查询类

    auto.on("select", select); //注册监听，当选中某条记录时会触发
    function select(e) {
        console.log(e.poi.location)
        placeSearch.setCity(e.poi.adcode);
        placeSearch.search(e.poi.name); //关键字查询查询
        var gcjLngLat = [e.poi.location.lng, e.poi.location.lat];
        console.log(gcjLngLat)
        searchfunc(gcjLngLat)
    }
});

// 选择后跳转 
function searchfunc(gcjLngLat) {
    currlng = gcjLngLat[0];
    currlat = gcjLngLat[1];
    document.getElementById("lng").value = currlng;
    document.getElementById("lat").value = currlat;
    geocoder.getAddress(gcjLngLat, function (status, result) {
        if (status === 'complete' && result.regeocode) {
            var address = result.regeocode.formattedAddress;

            // 更新坐标及地图位置
            marker.setPosition(gcjLngLat);
            marker.setTitle("GCJ: " + gcjLngLat);
            marker.setLabel({
                content: "<div id='label'>" + address + "</div>"
            });

        } else {
            console.log('根据经纬度查询地址失败...')
        }
    });

    var data = getBounds(gcjLngLat);
    polygon.setPath(data);
    var zoom = getZoom()
    map.setZoomAndCenter(zoom, gcjLngLat, false)
}



//绑定radio点击事件
var radios = document.querySelectorAll("#map-styles input");
radios.forEach(function (ratio) {
    ratio.onclick = setMapStyle;
});



function setMapStyle() {
    var styleName = "amap://styles/" + this.value;
    map.setMapStyle(styleName);
}


//设置地图显示要素
function setMapFeatures() {
    var features = [];
    var inputs = document.querySelectorAll("#map-features input");
    inputs.forEach(function (input) {
        if (input.checked) {
            features.push(input.value);
        }
    });
    map.setFeatures(features);
}

//绑定checkbox点击事件
var inputs = document.querySelectorAll("#map-features input");
inputs.forEach(function (checkbox) {
    checkbox.onclick = setMapFeatures;
});



function degree2radians(degree) {
    return degree * (Math.PI / 180);
}

function radians2degree(radians) {
    return radians * (180 / Math.PI);
}

function lnglat2xyz(lng, lat, z) {
    var n = Math.pow(2, z);
    var x = parseInt((lng + 180.0) / 360.0 * n);
    var lat_rad = degree2radians(lat);
    var y = parseInt((1.0 - Math.asinh(Math.tan(lat_rad)) / Math.PI) / 2.0 * n);

    return [x, y, z];
}

function xyz2lnglat(x, y, z) {
    var n = Math.pow(2, z);
    var lng = x / n * 360.0 - 180.0;

    var lat_rad = Math.atan(Math.sinh(Math.PI * (1 - 2 * y / n)))
    var lat = radians2degree(lat_rad);
    return [lng, lat];
}

function zoom2size(zoom) {
    return 78271516 * Math.pow(2, -zoom - 1);
}

function mct2lnglat(mct, origin) {
    var x = mct[0] / mercator;
    var y = mct[1] / mercator;

    y = 180 / Math.PI * (2 * Math.atan(Math.exp(y * Math.PI / 180)) - Math.PI / 2);
    x += origin[0];
    y += origin[1];

    return [x, y];
}

function getLngLat(e) {
    return [e.lnglat.getLng(), e.lnglat.getLat()];
};

function refreshLngLat(e) {
    var gcjLngLat = getLngLat(e);

    document.getElementById("lng").value = gcjLngLat[0];
    document.getElementById("lat").value = gcjLngLat[1];
};


// zoom 变化函数 
function zoomChanged() {
    var data = getBounds([currlng, currlat]);
    polygon.setPath(data);
};


// 获取 zoom 值 
function getZoom() {
    if (document.getElementById("zoom").value) { return parseInt(document.getElementById("zoom").value) }
    else { return defaultZoom }
}

// 瓦片 变化函数  
function getQuantity() {
    return parseInt(document.getElementById("quantity").value)
}


function quantityChanged() {

    var data = getBounds([currlng, currlat]);
    polygon.setPath(data);
}



function getBounds(lnglat) {
    var quantity = getQuantity();
    var zoom = getZoom();
    var xyz = lnglat2xyz(lnglat[0], lnglat[1], zoom);
    var origin = xyz2lnglat(xyz[0], xyz[1], xyz[2]);

    var size = zoom2size(zoom);


    var p1 = [size * quantity / 2, size * quantity / 2];
    var p2 = [size * quantity / 2, -size * quantity / 2];
    var p3 = [-size * quantity / 2, -size * quantity / 2];
    var p4 = [-size * quantity / 2, size * quantity / 2];

    var lnglat1 = mct2lnglat(p1, origin);
    var lnglat2 = mct2lnglat(p2, origin);
    var lnglat3 = mct2lnglat(p3, origin);
    var lnglat4 = mct2lnglat(p4, origin);

    return [lnglat1, lnglat2, lnglat3, lnglat4];
}


function onNumberChanged() {
    var lng = parseInt(document.getElementById("lng").value);
    var lat = parseInt(document.getElementById("lat").value);
    var data = getBounds([lng, lat]);
    polygon.setPath(data);
}

// 创建新地图
var map = new AMap.Map('container', {
    rotateEnable: true,
    pitchEnable: true,
    pitch: 50,
    rotation: -15,
    viewMode: '3D', //开启3D视图,默认为关闭
    center: defaultLocation,
    zooms: [2, 20],
    zoom: defaultZoom
});

var data = getBounds(defaultLocation);

var polygon = new AMap.Polygon({
    path: data,
    fillColor: '#ccebc5',
    strokeOpacity: 1,
    fillOpacity: 0.5,
    strokeColor: '#2b8cbe',
    strokeWeight: 1,
    strokeStyle: 'dashed',
    strokeDasharray: [5, 5],
});
polygon.on('mouseover', () => {
    polygon.setOptions({
        fillOpacity: 0.7,
        fillColor: '#7bccc4'
    })
})
polygon.on('mouseout', () => {
    polygon.setOptions({
        fillOpacity: 0.5,
        fillColor: '#ccebc5'
    })
})
map.add(polygon);

// 添加 3D 地图控件
var controlBar = new AMap.ControlBar({
    position: {
        right: '40px',
        top: '40px'
    }
});
controlBar.addTo(map);

var geocoder = new AMap.Geocoder({});

// 设置点击标记
var marker = new AMap.Marker({
    position: defaultLocation,
    icon: 'https://a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-default.png',
    anchor: 'bottom-center',
    offset: new AMap.Pixel(0, 0),
    draggable: true
});

// 设置label标签
// label默认蓝框白底左上角显示，样式className为：amap-marker-label
marker.setLabel({
    direction: 'center',
    offset: new AMap.Pixel(10, 0), //设置文本标注偏移量
    content: "<div id='label'>中建五局设计技术科研院 vctcn93</div>", //设置文本标注内容
});

// 将标记加入地图
marker.setMap(map);



// 点击事件函数
function clickfunc(e) {
    // 更新坐标及地图位置
    var gcjLngLat = getLngLat(e);
    currlng = gcjLngLat[0];
    currlat = gcjLngLat[1];
    document.getElementById("lng").value = currlng;
    document.getElementById("lat").value = currlat;
    geocoder.getAddress(gcjLngLat, function (status, result) {
        if (status === 'complete' && result.regeocode) {
            var address = result.regeocode.formattedAddress;

            // 更新坐标及地图位置
            marker.setPosition(gcjLngLat);

            marker.setTitle("GCJ: " + gcjLngLat);
            marker.setLabel({
                content: "<div id='label'>" + address + "</div>"
            });

        } else {
            console.log('根据经纬度查询地址失败...')
        }
    });

    var data = getBounds(gcjLngLat);
    polygon.setPath(data);
    console.log(data);
    map.setFitView();

}

// 拖拽事件函数
function dragendfunc(e) {
    // 更新坐标及地图位置

    var gcjLngLat = getLngLat(e);
    currlng = gcjLngLat[0];
    currlat = gcjLngLat[1];
    document.getElementById("lng").value = currlng;
    document.getElementById("lat").value = currlat;
    geocoder.getAddress(gcjLngLat, function (status, result) {
        if (status === 'complete' && result.regeocode) {
            var address = result.regeocode.formattedAddress;

            // 更新坐标及地图位置
            marker.setPosition(gcjLngLat);

            marker.setTitle("GCJ: " + gcjLngLat);
            marker.setLabel({
                content: "<div id='label'>" + address + "</div>"
            });

        } else {
            console.log('根据经纬度查询地址失败...')
        }
    });

    var data = getBounds(gcjLngLat);
    polygon.setPath(data);
    map.setFitView();

};

map.on('click', clickfunc);
marker.on('dragend', dragendfunc);
