#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 @File       : utils.py
 @Time       : 2018/4/23 0023 20:28
 @Author     : Empty Chan
 @Contact    : chen19941018@gmail.com
 @Description:
"""
import execjs

JS_CODE = """
// 第一层加密
    function f(e) {
        var t, r = [];
        for (r[(e.length >> 2) - 1] = void 0,
        t = 0; t < r.length; t += 1)
            r[t] = 0;
        var n = 8 * e.length;
        for (t = 0; t < n; t += 8)
            r[t >> 5] |= (255 & e.charCodeAt(t / 8)) << t % 32;
        return r
    }
        
// 第二层加密
        function p(e, t) {
            var r, n, o, a, p;
            e[t >> 5] |= 128 << t % 32,
            e[14 + (t + 64 >>> 9 << 4)] = t;
            var d = 1732584193
              , f = -271733879
              , g = -1732584194
              , h = 271733878;
            for (r = 0; r < e.length; r += 16)
                n = d,
                o = f,
                a = g,
                p = h,
                f = l(f = l(f = l(f = l(f = u(f = u(f = u(f = u(f = c(f = c(f = c(f = c(f = s(f = s(f = s(f = s(f, g = s(g, h = s(h, d = s(d, f, g, h, e[r], 7, -680876936), f, g, e[r + 1], 12, -389564586), d, f, e[r + 2], 17, 606105819), h, d, e[r + 3], 22, -1044525330), g = s(g, h = s(h, d = s(d, f, g, h, e[r + 4], 7, -176418897), f, g, e[r + 5], 12, 1200080426), d, f, e[r + 6], 17, -1473231341), h, d, e[r + 7], 22, -45705983), g = s(g, h = s(h, d = s(d, f, g, h, e[r + 8], 7, 1770035416), f, g, e[r + 9], 12, -1958414417), d, f, e[r + 10], 17, -42063), h, d, e[r + 11], 22, -1990404162), g = s(g, h = s(h, d = s(d, f, g, h, e[r + 12], 7, 1804603682), f, g, e[r + 13], 12, -40341101), d, f, e[r + 14], 17, -1502002290), h, d, e[r + 15], 22, 1236535329), g = c(g, h = c(h, d = c(d, f, g, h, e[r + 1], 5, -165796510), f, g, e[r + 6], 9, -1069501632), d, f, e[r + 11], 14, 643717713), h, d, e[r], 20, -373897302), g = c(g, h = c(h, d = c(d, f, g, h, e[r + 5], 5, -701558691), f, g, e[r + 10], 9, 38016083), d, f, e[r + 15], 14, -660478335), h, d, e[r + 4], 20, -405537848), g = c(g, h = c(h, d = c(d, f, g, h, e[r + 9], 5, 568446438), f, g, e[r + 14], 9, -1019803690), d, f, e[r + 3], 14, -187363961), h, d, e[r + 8], 20, 1163531501), g = c(g, h = c(h, d = c(d, f, g, h, e[r + 13], 5, -1444681467), f, g, e[r + 2], 9, -51403784), d, f, e[r + 7], 14, 1735328473), h, d, e[r + 12], 20, -1926607734), g = u(g, h = u(h, d = u(d, f, g, h, e[r + 5], 4, -378558), f, g, e[r + 8], 11, -2022574463), d, f, e[r + 11], 16, 1839030562), h, d, e[r + 14], 23, -35309556), g = u(g, h = u(h, d = u(d, f, g, h, e[r + 1], 4, -1530992060), f, g, e[r + 4], 11, 1272893353), d, f, e[r + 7], 16, -155497632), h, d, e[r + 10], 23, -1094730640), g = u(g, h = u(h, d = u(d, f, g, h, e[r + 13], 4, 681279174), f, g, e[r], 11, -358537222), d, f, e[r + 3], 16, -722521979), h, d, e[r + 6], 23, 76029189), g = u(g, h = u(h, d = u(d, f, g, h, e[r + 9], 4, -640364487), f, g, e[r + 12], 11, -421815835), d, f, e[r + 15], 16, 530742520), h, d, e[r + 2], 23, -995338651), g = l(g, h = l(h, d = l(d, f, g, h, e[r], 6, -198630844), f, g, e[r + 7], 10, 1126891415), d, f, e[r + 14], 15, -1416354905), h, d, e[r + 5], 21, -57434055), g = l(g, h = l(h, d = l(d, f, g, h, e[r + 12], 6, 1700485571), f, g, e[r + 3], 10, -1894986606), d, f, e[r + 10], 15, -1051523), h, d, e[r + 1], 21, -2054922799), g = l(g, h = l(h, d = l(d, f, g, h, e[r + 8], 6, 1873313359), f, g, e[r + 15], 10, -30611744), d, f, e[r + 6], 15, -1560198380), h, d, e[r + 13], 21, 1309151649), g = l(g, h = l(h, d = l(d, f, g, h, e[r + 4], 6, -145523070), f, g, e[r + 11], 10, -1120210379), d, f, e[r + 2], 15, 718787259), h, d, e[r + 9], 21, -343485551),
                d = i(d, n),
                f = i(f, o),
                g = i(g, a),
                h = i(h, p);
            return [d, f, g, h]
        }
// 依赖i, a, s, c, u, l
        function i(e, t) {
            var r = (65535 & e) + (65535 & t);
            return (e >> 16) + (t >> 16) + (r >> 16) << 16 | 65535 & r
        }
        
        function a(e, t, r, n, o, a) {
            return i((s = i(i(t, e), i(n, a))) << (c = o) | s >>> 32 - c, r);
            var s, c
        }
        function s(e, t, r, n, o, i, s) {
            return a(t & r | ~t & n, e, t, o, i, s)
        }
        
        function c(e, t, r, n, o, i, s) {
            return a(t & n | r & ~n, e, t, o, i, s)
        }
        function u(e, t, r, n, o, i, s) {
            return a(t ^ r ^ n, e, t, o, i, s)
        }
        function l(e, t, r, n, o, i, s) {
            return a(r ^ (t | ~n), e, t, o, i, s)
        }
        function m(e) {
            return function(e) {
                return d(p(f(e), 8 * e.length))
            }(h(e))
        }
// 第三层加密
        function d(e) {
            var t, r = "", n = 32 * e.length;
            for (t = 0; t < n; t += 8)
                r += String.fromCharCode(e[t >> 5] >>> t % 32 & 255);
            return r
        }
        function h(e) {
            return unescape(encodeURIComponent(e))
        }
        function g(e) {
            var t, r, n = "";
            for (r = 0; r < e.length; r += 1)
                t = e.charCodeAt(r),
                n += "0123456789abcdef".charAt(t >>> 4 & 15) + "0123456789abcdef".charAt(15 & t);
            return n
        }
        function b(e, t) {
            return function(e, t) {
                var r, n, o = f(e), i = [], a = [];
                for (i[15] = a[15] = void 0,
                o.length > 16 && (o = p(o, 8 * e.length)),
                r = 0; r < 16; r += 1)
                    i[r] = 909522486 ^ o[r],
                    a[r] = 1549556828 ^ o[r];
                return n = p(i.concat(f(t)), 512 + 8 * t.length),
                d(p(a.concat(n), 640))
            }(h(e), h(t))
        }
// 主函数
        function get_gis(e, t, r) {
            return t ? r ? b(t, e) : g(b(t, e)) : r ? m(e) : g(m(e))
        }
"""

ctx = execjs.compile(JS_CODE)


if __name__ == '__main__':
    gis = ctx.call('get_gis', '6c7abbf1ba29330f487c205e995f2585:{"id":"1179476381","first":12,"after":"AQCzte9xHs6-4YyZ182AQ38nmwSPtBmBNMUSNPNXoEygMkoxW5i811BcutQqoXmM5mJTYGZZyRc6qAnDmXSJtomxvkMyfsHqSTUFsw8GevJYcQ"}')
    print(gis)