import React from "react";
import {
  Card,
  CardMedia,
  CardContent,
  Typography,
  CardActions,
  Button,
} from "@mui/material";

const Membercard = ({ name, role, image, description, onMoreInfo }) => {
  return (
    <Card sx={{ maxWidth: 240, borderRadius: "16px", boxShadow: 3 }}>
      <CardMedia
        component="img"
        height="180"
        image={image}
        alt={`${name}'s profile`}
        sx={{ borderRadius: "16px 16px 0 0" }}
      />
      <CardContent>
        <Typography
          gutterBottom
          variant="h5"
          component="div"
          sx={{ fontWeight: "bold" }}
        >
          {name}
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          {role}
        </Typography>
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ marginTop: 1.5 }}
        >
          {description}
        </Typography>
      </CardContent>
      <CardActions
        sx={{
          display: "flex", // Flexbox 사용
          justifyContent: "center", // 가로 가운데 정렬
          alignItems: "center", // 세로 가운데 정렬
          gap: 1, // 버튼 간 간격
        }}
      >
        <Button size="small" onClick={onMoreInfo}>
          More Info
        </Button>
        <Button size="small" color="primary" variant="contained">
          Contact
        </Button>
      </CardActions>
    </Card>
  );
};

export default Membercard;
