const NodeCache = require('node-cache');

class CacheManager {
    constructor(ttlSeconds = 1800) {
        this.cache = new NodeCache({
            stdTTL: ttlSeconds,
            checkperiod: ttlSeconds * 0.2,
            useClones: false
        });
    }

    get(key) {
        return this.cache.get(key);
    }

    set(key, value, ttl) {
        return this.cache.set(key, value, ttl);
    }

    del(key) {
        return this.cache.del(key);
    }

    flush() {
        return this.cache.flushAll();
    }

    getStats() {
        return this.cache.getStats();
    }

    has(key) {
        return this.cache.has(key);
    }

    getTTL(key) {
        return this.cache.getTtl(key);
    }
}

module.exports = new CacheManager(process.env.CACHE_TTL || 1800);
