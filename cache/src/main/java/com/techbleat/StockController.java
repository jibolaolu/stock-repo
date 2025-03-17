package com.techbleat;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

import java.util.Map;


@RestController
@RequestMapping("/api/stocks")
public class StockController {

    @Autowired
    private StockService stockService;

    @GetMapping("/{ticker}/{date}")
    public ResponseEntity<?> getCache(@PathVariable String ticker, @PathVariable String date) {
        String cacheKey = ticker + ":" + date;
        if (date == null) {
            date = LocalDate.now().minusDays(1).format(DateTimeFormatter.ISO_DATE); // Default to yesterday
        }
        String price = stockService.getStockPrice(ticker, date);
        if (price == null)
              return ResponseEntity.status(HttpStatus.NOT_FOUND)
                                 .body(Map.of("error", "Cache not found for ticker " + ticker + " on " + date));
        
        return ResponseEntity.ok(price);  
    }

    @PostMapping("/save")
    public Double saveStockPrice(@RequestParam String ticker,
                                 @RequestParam String date,
                                 @RequestParam Double price) {
        return stockService.saveStockPrice(ticker, date, price);
    }

    @DeleteMapping("/delete")
    public String deleteStockCache(@RequestParam String ticker,
                                   @RequestParam String date) {
        stockService.deleteCache(ticker, date);
        return "Cache deleted for ticker " + ticker + " on " + date;
    }
}

