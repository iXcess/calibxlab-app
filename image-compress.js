/**
 * Client-side image compression for GitHub Pages → Apps Script (GET payload limits).
 */
(function (global) {
  var DEFAULTS = {
    maxWidth: 1400,
    maxHeight: 1400,
    maxBytes: 70000,
    mimeType: 'image/jpeg',
    quality: 0.82,
    minQuality: 0.42
  };

  function extForMime(mime) {
    if (mime === 'image/png') return '.png';
    if (mime === 'image/webp') return '.webp';
    return '.jpg';
  }

  function blobToBase64(blob) {
    return new Promise(function (resolve, reject) {
      var r = new FileReader();
      r.onload = function () {
        var parts = String(r.result || '').split(',');
        resolve(parts[1] || '');
      };
      r.onerror = function () { reject(new Error('Could not read compressed image')); };
      r.readAsDataURL(blob);
    });
  }

  function canvasToBlob(canvas, type, quality) {
    return new Promise(function (resolve) {
      canvas.toBlob(function (b) { resolve(b); }, type, quality);
    });
  }

  function drawToCanvas(img, maxW, maxH) {
    var w = img.naturalWidth || img.width;
    var h = img.naturalHeight || img.height;
    if (!w || !h) throw new Error('Invalid image dimensions');
    var scale = Math.min(1, maxW / w, maxH / h);
    w = Math.max(1, Math.round(w * scale));
    h = Math.max(1, Math.round(h * scale));
    var canvas = document.createElement('canvas');
    canvas.width = w;
    canvas.height = h;
    var ctx = canvas.getContext('2d');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, w, h);
    ctx.drawImage(img, 0, 0, w, h);
    return canvas;
  }

  function loadImageFromFile(file) {
    return new Promise(function (resolve, reject) {
      var url = URL.createObjectURL(file);
      var img = new Image();
      img.onload = function () {
        URL.revokeObjectURL(url);
        resolve(img);
      };
      img.onerror = function () {
        URL.revokeObjectURL(url);
        reject(new Error('Could not load image'));
      };
      img.src = url;
    });
  }

  function loadImageFromDataUrl(dataUrl) {
    return new Promise(function (resolve, reject) {
      var img = new Image();
      img.onload = function () { resolve(img); };
      img.onerror = function () { reject(new Error('Could not load signature')); };
      img.src = dataUrl;
    });
  }

  function compressCanvas(canvas, opts) {
    var mime = opts.mimeType || DEFAULTS.mimeType;
    var quality = opts.quality != null ? opts.quality : DEFAULTS.quality;
    var minQ = opts.minQuality != null ? opts.minQuality : DEFAULTS.minQuality;
    var maxBytes = opts.maxBytes != null ? opts.maxBytes : DEFAULTS.maxBytes;

    return canvasToBlob(canvas, mime, quality).then(function (blob) {
      if (!blob) throw new Error('Compression failed');
      function step() {
        if (blob.size <= maxBytes || quality <= minQ) return Promise.resolve(blob);
        quality = Math.max(minQ, quality - 0.08);
        return canvasToBlob(canvas, mime, quality).then(function (b) {
          blob = b || blob;
          return step();
        });
      }
      return step();
    }).then(function (blob) {
      return blobToBase64(blob).then(function (base64) {
        return {
          base64: base64,
          mimeType: mime,
          byteSize: blob.size
        };
      });
    });
  }

  function mergeOpts(overrides) {
    var o = {};
    Object.keys(DEFAULTS).forEach(function (k) { o[k] = DEFAULTS[k]; });
    if (overrides) Object.keys(overrides).forEach(function (k) { o[k] = overrides[k]; });
    return o;
  }

  /** Compress a receipt/photo File (images only). PDFs pass through with size cap. */
  global.calixlabCompressReceiptFile = function (file, overrides) {
    var opts = mergeOpts(overrides);
    if (!file) return Promise.reject(new Error('No file selected'));

    if (file.type === 'application/pdf') {
      var pdfMax = opts.pdfMaxBytes || 90000;
      if (file.size > pdfMax) {
        return Promise.reject(new Error(
          'PDF is too large (' + Math.round(file.size / 1024) + ' KB). Use a smaller file or photograph the receipt as JPG/PNG.'
        ));
      }
      return new Promise(function (resolve, reject) {
        var r = new FileReader();
        r.onload = function (e) {
          var base64 = String(e.target.result || '').split(',')[1] || '';
          resolve({
            base64: base64,
            mimeType: file.type,
            fileName: file.name,
            byteSize: file.size
          });
        };
        r.onerror = function () { reject(new Error('Could not read PDF')); };
        r.readAsDataURL(file);
      });
    }

    if (!file.type || file.type.indexOf('image/') !== 0) {
      return Promise.reject(new Error('Please upload JPG, PNG, or PDF.'));
    }

    return loadImageFromFile(file).then(function (img) {
      var canvas = drawToCanvas(img, opts.maxWidth, opts.maxHeight);
      return compressCanvas(canvas, opts);
    }).then(function (out) {
      var base = (file.name || 'receipt').replace(/\.[^.]+$/, '');
      return {
        base64: out.base64,
        mimeType: out.mimeType,
        fileName: base + extForMime(out.mimeType),
        byteSize: out.byteSize
      };
    });
  };

  /** Compress signature canvas export (PNG data URL → JPEG). */
  global.calixlabCompressSignatureDataUrl = function (dataUrl, overrides) {
    var opts = mergeOpts(Object.assign({
      maxWidth: 800,
      maxHeight: 400,
      maxBytes: 35000,
      quality: 0.88
    }, overrides || {}));

    return loadImageFromDataUrl(dataUrl).then(function (img) {
      var canvas = drawToCanvas(img, opts.maxWidth, opts.maxHeight);
      return compressCanvas(canvas, opts);
    }).then(function (out) {
      return {
        base64: out.base64,
        mimeType: out.mimeType,
        byteSize: out.byteSize
      };
    });
  };
})(typeof window !== 'undefined' ? window : this);
