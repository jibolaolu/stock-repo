package com.techbleat;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.cache.annotation.CachePut;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

@Service
@EnableCaching
public class StockService {

    @Autowired
    private StringRedisTemplate redisTemplate;

    private static final String STOCK_CACHE_PREFIX = "stock:";

    // Read the cache for a specific ticker and date
    @Cacheable(value = "stockPrices", key = "#ticker + ':' + #date")
    public String getStockPrice(String ticker, String date) {
        String cacheKey = STOCK_CACHE_PREFIX + ticker + ":" + date;
        
        // If the value is already cached, it will be returned from cache
        if (redisTemplate.hasKey(cacheKey)) {
            String cachedPrice = redisTemplate.opsForValue().get(cacheKey);
            return cachedPrice != null ? cachedPrice : null;
        }
        return null;
    }

    // Write the stock price to cache manually
    @CachePut(value = "stockPrices", key = "#ticker + ':' + #date")
    public Double saveStockPrice(String ticker, String date, Double price) {
        String cacheKey = STOCK_CACHE_PREFIX + ticker + ":" + date;
        redisTemplate.opsForValue().set(cacheKey, price.toString());
        return price;
    }

    // Delete cache entry
    public void deleteCache(String ticker, String date) {
        String cacheKey = STOCK_CACHE_PREFIX + ticker + ":" + date;
        redisTemplate.delete(cacheKey);
    }
}

