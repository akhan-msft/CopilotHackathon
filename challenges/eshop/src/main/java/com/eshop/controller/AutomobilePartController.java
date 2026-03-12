package com.eshop.controller;

import com.eshop.model.AutomobilePart;
import com.eshop.repository.AutomobilePartRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/parts")
@CrossOrigin(origins = "*")
public class AutomobilePartController {

    @Autowired
    private AutomobilePartRepository repository;

    @GetMapping
    public ResponseEntity<Map<String, Object>> getParts(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int limit,
            @RequestParam(required = false) String search,
            @RequestParam(required = false) Double minPrice,
            @RequestParam(required = false) Double maxPrice) {

        List<AutomobilePart> all;

        if (search != null && !search.isBlank()) {
            all = repository.search(search);
        } else {
            all = repository.findAll();
        }

        if (minPrice != null) {
            all = all.stream().filter(p -> p.getPrice() >= minPrice).toList();
        }
        if (maxPrice != null) {
            all = all.stream().filter(p -> p.getPrice() <= maxPrice).toList();
        }

        int total = all.size();
        int fromIndex = Math.min(page * limit, total);
        int toIndex = Math.min(fromIndex + limit, total);
        List<AutomobilePart> pageData = all.subList(fromIndex, toIndex);

        Map<String, Object> response = new HashMap<>();
        response.put("data", pageData);
        response.put("total", total);
        response.put("page", page);
        response.put("limit", limit);
        response.put("totalPages", (int) Math.ceil((double) total / limit));

        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<AutomobilePart> getPartById(@PathVariable int id) {
        return repository.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}
