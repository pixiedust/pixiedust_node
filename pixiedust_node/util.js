var Util = {
  /**
   * The iteration cache which will store iterated nodes
   */
  _iterCache: [],

  _isArray: function (item) {
    return Object.prototype.toString.call(item) === '[object Array]'
  },

  _isObject: function (item) {
    return Object.prototype.toString.call(item) === '[object Object]'
  },

  _isUndefined: function (item) {
    return typeof item === 'undefined';
  },

  /**
   * Stringify the given item.
   * If the item has circular references, the circular references
   * will be marked as [CIRCULAR REFERENCE]
   */
  _stringify: function (item) {
    var cache = [];

    return JSON.stringify(item, function (key, value) {
      if (typeof value === 'object' && value !== null) {
        if (cache.indexOf(value) !== -1) {
          // Found circular reference
          return '[CIRCULAR REFERENCE]';
        }

        cache.push(value);
        return value;
      }

      return value;
    });
  },

  _deepEqualLog: function (title, path, actual, expected) {
    title = title || '';
    path = path || [];
    return title + ' ' + path.join(" -> ") + ' | actual: ' + Util._stringify(actual) + ', expected: ' + Util._stringify(expected);
  },

  _doDeepEqual: function (actual, expected, notEqualCallback, path) {
    var iter;

    notEqualCallback = notEqualCallback || function () {};
    path = path || [];

    if (Util._iterCache.indexOf(actual) !== -1) {
      // We have iterated this node before and it passed deep equal check
      return true;
    }

    // Primitive type
    if (actual === expected) {
      return true;
    }

    // NaN
    if (Number.isNaN(actual) && Number.isNaN(expected)) {
      return true;
    } else if (Number.isNaN(actual) || Number.isNaN(expected)) {
      notEqualCallback(Util._deepEqualLog('[Value different]', path, actual, expected));
      return false;
    }

    // Array
    if (Util._isArray(actual) && Util._isArray(expected)) {
      iter = actual.length;
      if (iter !== expected.length) {
        notEqualCallback(Util._deepEqualLog('[Array with different length]', path, actual, expected));
        return false;
      }

      // Mark the actual and expected array has been iterated
      Util._iterCache.push(actual);
      while (iter--) {
        if (!Util._doDeepEqual(actual[iter], expected[iter], notEqualCallback, path.concat(iter))) {
          return false;
        }
      }

      return true;
    } else if (Util._isArray(actual) || Util._isArray(expected)) {
      notEqualCallback(Util._deepEqualLog('[Different type]', path, actual, expected));
      return false;
    }

    // Object
    if (Util._isObject(actual) && Util._isObject(expected)) {
      if (Object.keys(actual).length !== Object.keys(expected).length) {
        notEqualCallback(Util._deepEqualLog('[Object with different keys]', path, actual, expected));
        return false;
      }

      // Mark the actual and expected array has been iterated
      Util._iterCache.push(actual);
      for (iter in actual) {
        if (actual.hasOwnProperty(iter)) {
          if (!Util._doDeepEqual(actual[iter], expected[iter], notEqualCallback, path.concat(iter))) {
            return false;
          }
        }
      }

      return true;
    } else if (Util._isObject(actual) || Util._isObject(expected)) {
      notEqualCallback(Util._deepEqualLog('[Different type]', path, actual, expected));
      return false;
    }

    // Default to false
    notEqualCallback(Util._deepEqualLog('[Value different]', path, actual, expected));
    return false;
  },

  /**
   * Check the deep equal for primitive type values, array and objects.
   * The native assert.deepEqual doesn't work well for NaN case as well
   * as +0/-0 case. See https://github.com/substack/node-deep-equal for
   * more details
   */
  deepEqual: function (actual, expected, notEqualCallback) {
    notEqualCallback = notEqualCallback || function () {};
    Util._iterCache = [];
    return Util._doDeepEqual(actual, expected, notEqualCallback);
  },

  /**
   * Compare and return both the deep equal results, as well as the not equal message
   */
  deepEqualWithMessage: function (actual, expected) {
    var notEqualMessages = [],
        isDeepEqual = Util.deepEqual(actual, expected, function () {
          notEqualMessages.push(Array.prototype.slice.call(arguments).join(''));
        });

    return {
      isDeepEqual: isDeepEqual,
      message: notEqualMessages.join('\n')
    };
  }
};

module.exports = {
  deepEqual: Util.deepEqual,
  deepEqualWithMessage: Util.deepEqualWithMessage
};