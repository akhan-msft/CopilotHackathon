package com.eshop.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class AutomobilePart {
    private int id;
    private String name;
    private String description;

    @JsonProperty("image_url")
    private String imageUrl;

    private double price;
    private String manufacturer;

    @JsonProperty("model_compatibility")
    private List<String> modelCompatibility;

    @JsonProperty("part_number")
    private String partNumber;

    private int stock;
    private Specifications specifications;

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getImageUrl() { return imageUrl; }
    public void setImageUrl(String imageUrl) { this.imageUrl = imageUrl; }

    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }

    public String getManufacturer() { return manufacturer; }
    public void setManufacturer(String manufacturer) { this.manufacturer = manufacturer; }

    public List<String> getModelCompatibility() { return modelCompatibility; }
    public void setModelCompatibility(List<String> modelCompatibility) { this.modelCompatibility = modelCompatibility; }

    public String getPartNumber() { return partNumber; }
    public void setPartNumber(String partNumber) { this.partNumber = partNumber; }

    public int getStock() { return stock; }
    public void setStock(int stock) { this.stock = stock; }

    public Specifications getSpecifications() { return specifications; }
    public void setSpecifications(Specifications specifications) { this.specifications = specifications; }
}
