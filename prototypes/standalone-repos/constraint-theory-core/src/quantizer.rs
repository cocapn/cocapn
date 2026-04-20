//! Pythagorean quantization

/// Quantizes floating point to exact representations
pub struct PythagoreanQuantizer {
    precision: u32,
}

impl PythagoreanQuantizer {
    pub fn new(precision: u32) -> Self {
        Self { precision }
    }

    pub fn quantize(&self, value: f64) -> i64 {
        (value * (10_i64.pow(self.precision) as f64)).round() as i64
    }

    pub fn dequantize(&self, value: i64) -> f64 {
        value as f64 / (10_i64.pow(self.precision) as f64)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_quantize_dequantize() {
        let q = PythagoreanQuantizer::new(6);
        let original = 3.1415926535;
        let quantized = q.quantize(original);
        let back = q.dequantize(quantized);
        assert!((back - original).abs() < 1e-6);
    }
}
