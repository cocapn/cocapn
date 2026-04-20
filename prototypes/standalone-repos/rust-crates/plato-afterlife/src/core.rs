/// Core module placeholder
pub fn hello() -> &'static str {
    "Hello from CoCapn!"
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hello() {
        assert_eq!(hello(), "Hello from CoCapn!");
    }
}
