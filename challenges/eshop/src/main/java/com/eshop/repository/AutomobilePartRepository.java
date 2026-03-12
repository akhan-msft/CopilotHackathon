package com.eshop.repository;

import com.eshop.model.AutomobilePart;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Repository;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Repository
public class AutomobilePartRepository {

    private List<AutomobilePart> parts = new ArrayList<>();

    @PostConstruct
    public void loadData() throws Exception {
        ObjectMapper mapper = new ObjectMapper();
        InputStream is = getClass().getResourceAsStream("/data/automobileParts.json");
        parts = mapper.readValue(is, new TypeReference<List<AutomobilePart>>() {});
    }

    public List<AutomobilePart> findAll() {
        return parts;
    }

    public Optional<AutomobilePart> findById(int id) {
        return parts.stream().filter(p -> p.getId() == id).findFirst();
    }

    public List<AutomobilePart> search(String query) {
        String q = query.toLowerCase();
        return parts.stream()
                .filter(p -> p.getName().toLowerCase().contains(q)
                        || p.getDescription().toLowerCase().contains(q)
                        || p.getManufacturer().toLowerCase().contains(q)
                        || String.valueOf(p.getPrice()).contains(q))
                .toList();
    }
}
