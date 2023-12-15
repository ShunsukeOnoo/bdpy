from __future__ import annotations

from abc import ABC, abstractmethod

import torch
import torch.nn as nn


class BaseCritic(nn.Module, ABC):
    """Critic network module."""

    @abstractmethod
    def criterion(
        self, feature: torch.Tensor, target_feature: torch.Tensor, layer_name: str
    ) -> torch.Tensor:
        """Loss function per layer.

        Parameters
        ----------
        feature : torch.Tensor
            Feature tensor of the layer specified by `layer_name`.
        target_feature : torch.Tensor
            Target feature tensor of the layer specified by `layer_name`.
        layer_name : str
            Layer name.

        Returns
        -------
        torch.Tensor
            Loss value of the layer specified by `layer_name`.
        """
        pass

    def forward(
        self,
        features: dict[str, torch.Tensor],
        target_features: dict[str, torch.Tensor],
    ) -> torch.Tensor:
        """Forward pass through the critic network.

        Parameters
        ----------
        features : dict[str, torch.Tensor]
            Features indexed by the layer names.
        target_features : dict[str, torch.Tensor]
            Target features indexed by the layer names.

        Returns
        -------
        torch.Tensor
            Loss value.
        """
        loss = 0.0
        counts = 0
        for layer_name, feature in features.items():
            target_feature = target_features[layer_name]
            layer_wise_loss = self.criterion(
                feature, target_feature, layer_name=layer_name
            )
            loss += layer_wise_loss
            counts += 1
        return loss / counts


class TargetNormalizedMSE(BaseCritic):
    """MSE loss divided by the squared norm of the target feature."""

    def criterion(
        self, feature: torch.Tensor, target_feature: torch.Tensor, layer_name: str
    ) -> torch.Tensor:
        """Loss function per layer.

        Parameters
        ----------
        feature : torch.Tensor
            Feature tensor of the layer specified by `layer_name`.
        target_feature : torch.Tensor
            Target feature tensor of the layer specified by `layer_name`.
        layer_name : str
            Layer name.

        Returns
        -------
        torch.Tensor
            Loss value of the layer specified by `layer_name`.
        """
        squared_norm = (target_feature ** 2).sum(dim=tuple(range(1, target_feature.ndim)))
        return ((feature - target_feature) ** 2).sum(
            dim=tuple(range(1, feature.ndim))
        ) / squared_norm
