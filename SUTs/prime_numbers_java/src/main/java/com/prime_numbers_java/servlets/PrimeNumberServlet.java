package com.prime_numbers_java.servlets;

import jakarta.servlet.*;
import jakarta.servlet.http.*;
import java.io.*;
import java.util.ArrayList;
import java.util.List;

public class PrimeNumberServlet extends HttpServlet {
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        response.setHeader("Access-Control-Allow-Origin", "*"); // For development only
        response.setHeader("Access-Control-Allow-Methods", "POST");
        response.setHeader("Access-Control-Allow-Headers", "Content-Type");
        response.setContentType("application/json");
        PrintWriter out = response.getWriter();

        String resetParam = request.getParameter("reset");
        if ("true".equals(resetParam)) {
            request.getSession().setAttribute("lastPrime", null);
            out.print("{\"reset\": \"success\"}");
            out.flush();
            return;
        }

        String nextPrimeParam = request.getParameter("nextPrime");
        if ("true".equals(nextPrimeParam)) {
            out.print(getNextPrimeJson(request));
        } else {
            int limit = Integer.parseInt(request.getParameter("limit"));
            List<Integer> primes = calculatePrimes(limit);
            out.print(buildJsonResponse(primes));
        }

        out.flush();
    }

    private String getNextPrimeJson(HttpServletRequest request) {
        HttpSession session = request.getSession();
        Integer lastPrime = (Integer) session.getAttribute("lastPrime");
        if (lastPrime == null) {
            lastPrime = 1;
        }

        int nextPrime = findNextPrime(lastPrime);
        session.setAttribute("lastPrime", nextPrime);

        return "{\"nextPrime\": " + nextPrime + "}";
    }

    private List<Integer> calculatePrimes(int limit) {
        List<Integer> primes = new ArrayList<>();
        int count = 0;
        int number = 2;

        while (count < limit) {
            if (isPrime(number)) {
                primes.add(number);
                count++;
            }
            number++;
        }
        return primes;
    }

    private boolean isPrime(int number) {
        if (number <= 1) {
            return false;
        }
        for (int i = 2; i <= Math.sqrt(number); i++) {
            if (number % i == 0) {
                return false;
            }
        }
        return true;
    }

    private int findNextPrime(int after) {
        int number = after + 1;
        while (!isPrime(number)) {
            number++;
        }
        return number;
    }

    private String buildJsonResponse(List<Integer> primes) {
        StringBuilder jsonBuilder = new StringBuilder();
        jsonBuilder.append("{\"primes\": [");
        for (int i = 0; i < primes.size(); i++) {
            jsonBuilder.append(primes.get(i));
            if (i < primes.size() - 1) {
                jsonBuilder.append(", ");
            }
        }
        jsonBuilder.append("]}");
        return jsonBuilder.toString();
    }
}
